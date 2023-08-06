import wfront

ENVIRON = {'HTTP_HOST': '127.0.0.1',
           'PATH_INFO': '/',
           'REQUEST_METHOD': 'GET',
           'SCRIPT_NAME': '',
           'SERVER_NAME': '127.0.0.1',
           'SERVER_PORT': '80',
           'SERVER_PROTOCOL': 'HTTP/1.0',
           'wsgi.errors': None,
           'wsgi.input': None,
           'wsgi.multiprocess': 0,
           'wsgi.multithread': 0,
           'wsgi.run_once': 0,
           'wsgi.url_scheme': 'http',
           'wsgi.version': (1, 0)}

class wsgi_app(object):
    def __init__(self):
        self.ran = False
        self.environ = None

    def __call__(self, environ, start_response):
        self.ran = True
        self.environ = environ

    @staticmethod
    def reset(*apps):
        for a in apps:
            a.ran = False
            a.environ = None


def simple_env(host='localhost', path='/', script_name='',
               force_ssl=False, **kw):
    e = ENVIRON.copy()

    if not ':' in host:
        if not force_ssl:
            port = 80
        else:
            port = 443
    else:
        host, port = host.split(':', 2)
        port = int(port)

    if port not in (80, 443):
        e['HTTP_HOST'] = "%s:%u" % (host, port)
    else:
        e['HTTP_HOST'] = host

    e['SERVER_NAME'] = host
    e['SERVER_PORT'] = str(port)

    if port == 443 or force_ssl:
        e['wsgi.url_scheme'] = 'https'

    e['PATH_INFO'] = path
    e['SCRIPT_NAME'] = script_name

    e.update(**kw)
    return e

def test_glob():
    e = simple_env('localhost')
    matched = wsgi_app()

    wfront.route([('*', matched)])(e, None)

    assert matched.ran

def test_default():
    e = simple_env('localhost')

    matched, default  = wsgi_app(), wsgi_app()

    wfront.route([('localhost', matched)], default=default)(e, None)

    assert matched.ran
    assert not default.ran

    wsgi_app.reset(matched, default)

    wfront.route([('snaggletooth', matched)], default=default)(e, None)

    assert not matched.ran
    assert default.ran

def test_abort404():
    e = simple_env('localhost')

    matched, abort404  = wsgi_app(), wsgi_app()

    wfront.route([('*', matched)], abort404=abort404)(e, None)

    assert matched.ran
    assert not abort404.ran

    wsgi_app.reset(matched, abort404)

    wfront.route([('snaggletooth', matched)], abort404=abort404)(e, None)

    assert not matched.ran
    assert abort404.ran

    wsgi_app.reset(matched, abort404)
    default = wsgi_app()

    wfront.route([('snaggletooth', matched)],
                 abort404=abort404,
                 default=default)(e, None)

    assert not matched.ran
    assert default.ran
    assert not abort404.ran

def test_port80():
    e = simple_env('localhost')

    matched = wsgi_app()
    wfront.route([(':80', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([('*:80', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([('*:80:', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([('*:80:*', matched)])(e, None)
    assert matched.ran

def test_port443_1():
    e = simple_env('localhost', force_ssl=True)

    matched = wsgi_app()
    wfront.route([(':443', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([('*:443', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([(':443:', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([(':443:*', matched)])(e, None)
    assert matched.ran

def test_port443_2():
    # Don't let wsgi.url_scheme get set for this one:
    e = simple_env('localhost', SERVER_PORT='443', HTTPS='on')

    matched = wsgi_app()
    wfront.route([(':443', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([('*:443', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([(':443:', matched)])(e, None)
    assert matched.ran

    matched = wsgi_app()
    wfront.route([(':443:*', matched)])(e, None)
    assert matched.ran

def test_pathinfo():
    # No consumption if path is unspecified or blanket wildcarded
    for m in (':80', ':80:', ':80:*'):
        e = simple_env('localhost', path='/')
        matched = wsgi_app()
        wfront.route([(m, matched)])(e, None)
        assert matched.ran
        assert matched.environ['PATH_INFO'] == '/'
        assert matched.environ['SCRIPT_NAME'] == ''


    for m, scriptname, pathinfo in (('::/','/','pok:pok'),
                                    ('::/pok', '/pok', ':pok'),
                                    ('::/pok:', '/pok:', 'pok'),
                                    ('::/pok:pok', '/pok:pok', '')):
        e = simple_env('localhost', path='/pok:pok')
        matched = wsgi_app()
        wfront.route([(m, matched)])(e, None)
        assert matched.ran
        assert matched.environ['PATH_INFO'] == pathinfo
        assert matched.environ['SCRIPT_NAME'] == scriptname
