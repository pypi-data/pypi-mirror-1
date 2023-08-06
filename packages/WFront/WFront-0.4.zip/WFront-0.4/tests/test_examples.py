from wsgiref import util


def test_mod_proxy():
    import examples.apache.mod_proxy
    # TODO.  test import only for now.

def test_pound_1():
    from examples import pound

    environ = create_environ()
    r = wsgi_response(pound.front_door, environ)
    assert "HTTP_HOST\t'host1.domain'" in r, r

    environ = create_environ(HTTP_HOST='squiznart')
    r = wsgi_response(pound.front_door, environ)
    assert "HTTP_HOST\t'squiznart'" in r

def test_pound_2():
    from examples import pound

    environ = create_environ(HTTP_HOST='foo')
    r = wsgi_response(pound.front_door2, environ)
    assert "HTTP_HOST\t'foo'" in r, r

    environ = create_environ(HTTP_X_FALLBACK_HOST='squiznart')
    r = wsgi_response(pound.front_door2, environ)
    assert "HTTP_HOST\t'squiznart'" in r

def test_pound_3():
    from examples import pound

    environ = create_environ(HTTP_X_SCHEME='https')
    r = wsgi_response(pound.front_door3, environ)
    assert "wsgi.url_scheme\t'https'" in r


def create_environ(**kw):
    environ = dict(**kw)
    util.setup_testing_defaults(environ)
    if 'HTTP_HOST' not in kw:
        environ.pop('HTTP_HOST', None)
    return environ

def wsgi_response(app, environ):
    start_response = lambda status, headers: None
    response = app(environ, start_response)
    if hasattr(response, 'close'):
        response.close()
    return ''.join(response)

