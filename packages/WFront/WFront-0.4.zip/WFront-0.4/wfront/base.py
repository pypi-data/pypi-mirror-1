"""WSGI request routing.

:copyright: the WFront authors and developers, see AUTHORS.
:license: MIT, see LICENSE for more details.

"""
import operator
import os
import re
from wfront import rewriter
from wfront.resolvers import default_resolver, LogicalRouteResolver
from wfront._internal import (
    _abort404,
    _callableize,
    _demote_pathinfo,
    _glob,
    )


def route(mapping, **kw):
    """Create a routing middleware matching hostname, port and path.

    :param mapping: A sequence of mapping tuples, see :doc:`mappings`

    :param default: Optional. Invoked if there are no hits in the map. May
      either be a WSGI callable or a 2-tuple of (app, filter).

    :param host_resolver: a callable that receives an environ and returns a
      string of ``'hostname:port:path'``.  Defaults to
      :func:`~wfront.default_resolver`.

    :param abort404: a WSGI app that will be run if there are no map hits and
      no *default* is provided.  Default *abort404* is a very simple 404
      WSGI application.

    :param cleanup_syntax: may be ``verbose`` or ``shortcut``.  If
      ``shortcut``, enables shortcut filter specifications.  See
      :doc:`filter`.

    :param \*\*kw: passed through to :meth:`WFront.__init__`.

    Returns a :class:`~wfront.WFront` WSGI callable::

      router = wfront.route([('www.my.host:80', app, None)])

    """
    return WFront(mapping, **kw)

def by_scheme(mapping, schemes={'http': (80,), 'https': (443,)}, **kw):
    """Create a routing middleware matching hostname, URL scheme and path.

    :param mapping: A sequence of mapping tuples, see :doc:`mappings`

    :param schemes: A mapping of scheme names to sequences of port
      numbers.  By default, http on port 80 and https on 443.

    :param proxied_host_is_accurate: optional.  If False, a Host: header will
      not be considered if a X-Forwarded-For header is also present.  Only
      required for some non-transparent front-end proxy configurations.

    :param default: Optional. Invoked if there are no hits in the map. May
      either be a WSGI callable or a 2-tuple of (app, filter).

    :param abort404: a WSGI app that will be run if there are no map hits and
      no *default* is provided.  Default *abort404* is a very simple 404
      WSGI application.

    :param cleanup_syntax: may be ``verbose`` or ``shortcut``.  If
      ``shortcut``, enables shortcut filter specifications.

    :param \*\*kw: passed through to :meth:`WFront.__init__`.

    If you have a server that speaks HTTP on 80, 8000 and 8001, you
    might specify::

       router = wfront.by_scheme([('www.my.host:http', app, None)],
                                 schemes={'http': (80, 8000, 8001)})

    This would match on a request for ``www.my.host`` made to port 80,
    8000 or 8001.

    """
    resolver = LogicalRouteResolver(
        schemes, kw.pop('proxied_host_is_accurate', None))
    return WFront(mapping, host_resolver=resolver, **kw)

class WFront(object):
    def __init__(self, mapping, default=None, host_resolver=None,
                 abort404=None, cleanup_syntax='verbose'):
        """Create a routing middleware that directs to one or more WSGI apps.

        :param mapping: a mapping specification.

        :param default: Optional. Invoked if there are no hits in the map. May
          either be a WSGI callable or a 2-tuple of (app, filter).

        :param host_resolver: a callable that receives an environ and returns
          a string of ``':hostname:port:path'``.  Defaults to
          :func:`~wfront.default_resolver`.

        :param abort404: a WSGI app that will be run if there are no map hits
          and no *default* is provided.  Default is a very simple 404 handler.

        :param cleanup_syntax: may be ``verbose`` or ``shortcut``.  If
          ``shortcut``, enables shortcut filter specifications.

        A simple router that answers any request for ``localhost``::

          front = WFront([('localhost', myapp, None)])

        A more complex router::

          mapping = [ ('www.example.com', myapp),
                      ('www.example.com:443', sec_app, 'mymodule.filter'),
                      ('wap.example.mobi', myapp, {'mode': 'wap'}), ]

          router = WFront(mapping)

        By default, the requested host is taken from HTTP_HOST and guaranteed
        to contain a port number.  You can customize this behavior by
        supplying 'host_resolver' as a function that takes the environ and
        returns a string of 'hostname:port:path'

        """

        self.mapping      = []

        self.host_resolver = host_resolver or default_resolver

        if abort404 is None:
            self.abort404 = _abort404
        else:
            self.abort404 = _callableize(abort404)

        self.cleanup_syntax = cleanup_syntax

        if default:
            if type(default) is not tuple:
                default = (default, None)

            app, filter = default
            default = (_callableize(app), self._prepare_filter(filter))

        self.default        = default

        for spec in mapping:
            self.add(*spec)

    def __call__(self, environ, start_response):
        req = self.host_resolver(environ)
        if 'wsgiorg.routing_args' in environ:
            environ['wsgiorg.routing_args'][1]['wfront_match'] = req
        else:
            environ['wsgiorg.routing_args'] = ((), {'wfront_match': req})

        for r, app, filter in self.mapping:
            m = r.match(req)
            if m:
                if 'pathinfo' in m.groupdict():
                    _demote_pathinfo(environ, m.groupdict()['pathinfo'])
                break
        else:
            if self.default:
                app, filter = self.default
            else:
                return self.abort404(environ, start_response)

        if not filter:
            return app(environ, start_response)
        elif type(filter) is dict:
            environ.update(filter)
            return app(environ, start_response)
        else:
            return filter(app, environ, start_response)

    def add(self, spec, app, filter=None):
        """Add a new mapping.

        Spec may be a regex in which case it is used as-is, otherwise spec is
        regex-escaped and converted into a host:port:path matcher.

        If a regex is supplied and it contains a 'pathinfo' named group, that
        group will be used in PATH_INFO / SCRIPT_NAME manipulation.

        """
        if not spec:
            regex = re.compile(r'^')
        elif hasattr(spec, 'match'):
            regex = spec
        else:
            host, port, path = map(lambda a, b: a or b,
                                   spec.split(':', 2), (None, None, None))

            host = _glob(host) or '[^:]+'
            port = _glob(port) or '[^:]+'

            if not path or path == '*':
                path = '.*'
            else:
                path = '(?P<pathinfo>%s)' % _glob(path)

            regex = re.compile('^%s:%s:%s' % (host, port, path))

        self.mapping.append((regex,
                             _callableize(app),
                             self._prepare_filter(filter)))

    def _prepare_filter(self, filter):
        if not filter:
            return None
        elif type(filter) is dict:
            return self._builtin_cleanup_factory(
                filter, syntax=self.cleanup_syntax)
        else:
            return _callableize(filter)

    def dump_mappings(self):
        """Debugging, dump decompiled regex patterns."""

        return [r.pattern for r, _, _ in self.mapping]

    def _builtin_cleanup_factory(self, data, syntax='verbose'):
        """Given a cleanup dict, determines if this should be straight
        dict.update() or a directed merge.  Returns either a update()-suitable
        dict or a cleanup callable for use at request time.
        """
        if not data:
            return None
        if syntax == 'shortcut':
            pairs = rewriter.expand_shorthand(data)
        else:
            pairs = data

        rules = rewriter.EnvironRewriter(pairs)
        if len(data) == len(rules.replace):
            return data
        else:
            return rules.as_filter


class MacroMap(list):
    """Expands simple macros in routing specs.

    MacroMap is constructed with a simple mapping of short-name to long-name,
    expanding any references of the form ``{short-name}`` to ``long-name``::

      >>> from wfront import MacroMap
      >>> mm = MacroMap(macros={'domain': 'example.com'})
      >>> mm.add('{domain}:http', app)
      >>> mm.add('www.{domain}:http', app)

    Or in bulk:

      >>> expansions = {'domain': 'example.com'}
      >>> routes = [('{domain}', app), ('www.{domain}', app)]
      >>> mapping = MacroMap(routes, macros=expansions)
      >>> mapping
      [('example.com', app, None), ('www.example.com', app, None)]

    The non-standard syntax ``{}`` was chosen to avoid conflicts with
    definitions loaded from ConfigParser ``.ini`` files.

    """
    def __init__(self, sequence=None, macros={}):
        """Construct a MacroMap.

        :param sequence: optional, a sequence of 2 or 3 element tuples.  Each
          will be supplied positionally to :meth:`add`.

        :param macros: a mapping of ``short-name`` to ``long-name``.

        """
        self.macros = macros
        if sequence is not None:
            for item in sequence:
                if type(item) is not tuple:
                    raise ValueError(
                        'Mapping sequence must consist of tuples.')
                self.add(*item)

    def add(self, spec, app, filter=None):
        """Append a route from *spec* to *app*.

        :param spec: a routing specification.  May contain macro substitution
          tokens of the form ``{token}``.  Unmatched tokens will raise an
          error.

        :param app: a WSGI callable or string reference

        :param filter: optional, a mapping filter

        """
        self.append((self._expand(spec), app, filter))

    def _expand(self, spec):
        spec = re.sub(r'\{([^}]+)\}', r'%(\1)s', spec)
        return spec % self.macros


class PathMap(list):
    """A route mapping helper that sets up simple path-based routing.

    Routes are created with wildcarded host and port by default.  Useful for
    simple path forwarders::

      >>> from wfront import PathMap
      >>> pm = PathMap()
      >>> pm.add('/foo', app1)
      >>> pm.add('/', app2)

    Mappings can also be made by the constructor::

      >>> mapping = PathMap([('/foo', app1), ('/', app2)])
      >>> mapping
      [('*:*:/foo', app1, None), ('*:*:/', app2, None)]

    PathMap is syntactic sugar for normal 3-tuple mappings.  All features
    available to regular mappings are available to PathMap.

    """

    def __init__(self, sequence=None):
        """Construct a PathMap.

        :param sequence: Optional sequence of n-tuples.  Each will be supplied
          positionally to :meth:`add`.  Each n-tuple must contain at least 2
          members (``(path, app)``).

        """
        if sequence is not None:
            for item in sequence:
                self.add(*item)

    def add(self, path, app, filter=None, host='*', port='*'):
        """Append a route from *path* to *app*.

        :param path: a URL path to match

        :param app: a WSGI callable or string reference

        :param filter: optional, a mapping filter

        :param host: the host portion to match, by default ``*``

        :param port: the port portion to match, by default ``*``

        """
        matcher = ':'.join((host, port, path))
        self.append((matcher, app, filter))


def echo_app(environ, start_response):
    """A simple WSGI app that dumps the environ."""
    start_response('200 OK', [('Content-Type', 'text/plain')])
    output = []
    for key, value in sorted(environ.iteritems(), key=operator.itemgetter(0)):
        # ignore noise from servers like wsgiref that merge all of os.environ
        if key in os.environ:
            continue
        output.append("%s\t%r\n" % (key, value))
    return output
