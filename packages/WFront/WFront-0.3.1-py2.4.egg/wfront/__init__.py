# Copyright 2006 Jason Kirtland <jek at discorporate us>
"""
A WSGI front-door dispatcher.

WFront is a simple top-level request dispatcher, directing requests
based on "Virtual Host".  WFront can be used to host multiple
WSGI-powered domains in a single process, emulate a mod_proxy,
SCGI/FastCGI/AJP or mod_python WSGI setup for development, or any
other composition where operating at the host-level is desired.
Mapping HTTP/1.0 requests to HTTP/1.1 Host:-style requests is
supported and is very flexible.

Features
========

WFront was developed to unify 'development mode' WSGI servers and
Apache-fronted production WSGI servers connected via Apache
mod_proxy, FastCGI, AJP, etc.  The examples discuss Apache, but
WFront is not Apache-specific.

Some example routing situations WFront can assist with:

- Serve different applications based on the hostname the user requested.

- Provide cross-application, 'whole domain' services and
  configuration.

- Isolate your WSGI applications from deployment details- standard
  URL generation from environ can always work, no matter how the
  application is being hosted.  Smooth away details of listening on
  alternate ports, proxies, end-to-end vs. forwarded HTTPS, etc.

- Reliably service HTTP/1.0 Apache VirtualHosts in a mod_proxy environment.

- Use the same routing configuration in production and development:
  logical routing 'www.example.com' can be separated from
  server-specific proxy routing hackery.
  
- Run a single-process, multi-port, multi-domain development server
  process that mimics a production cluster deployment.

WFront provides 3 hooks into the request routing process:

1) Host: determination (pluggable)

   Analyze the environ and determine which VirtualHost and URI is
   being requested.  The default implementation handles direct and
   proxied requests automatically.

2) Routing

   Matches the incoming request information to a mapping of WSGI
   applications.

3) Cleanup (pluggable)

   Optional processing of environ and start_response before the WSGI
   application is invoked.  The default implementation allows you to
   perform useful environment manipulation in a dict-based interface.


Usage
=====
::

    map = [('www.example.com', myapp, None),
           ('www.example.com:3000', otherapp, {'environ.key':'value'}),]

    front = wfront.route(map)
    return front(environ, start_response)

    map = [('www.example.com:http', myapp, None),
           ('www.example.com:https', secureapp, None) ]

    front = wfront.by_scheme(map, schemes={'http':(80,), 'https':(443,3000)'})
    return front(environ, start_response)


WFront is driven by a routing map.  The mapping is a sequence of
3-tuples::

    path-spec, wsgi callable or string, pre-request cleanup

Path specs are compared to the requested hostname, port and path.
Any or all of these components can be matched against, either
literally or wildcarded.  Separate each component with a colon.
Empty or missing components match anything.
::

    www.example.com
    www.example.com:80
    www.example.com:80:/some/path
    *.example.com::/some/path
    :80
    ::/some/path

Two path spec extensions are provided to generalize configuration.

``wfront.by_scheme()`` maps ports to request schemes, allowing you to
route without tracking exactly which port(s) are currently bound::

    www.example.com:http
    secure.example.com:https

``MacroMap`` adds simple macro expansion to path specs::

    www.{domain}
    secure.{domain}

The WSGI application to dispatch to may be supplied either as a
callable or a string.  Strings are passed to either ``resolver`` or
``Paste`` for evaluation and are expected to return a callable.  See
either package's documentation for details, but the general idea is
something like::

    'module:my_callable'

You must have either ``resolver`` and/or the ``Paste`` package
installed to use this feature.

Pre-request cleanup is an optional filter that operates on the WSGI
call arguments: environ and start_response.  As a convenience, you
may provide a ``dict`` of key/value pairs instead of a callable and
they will be merged into the ``environ`` dict on each request.  You
may also specify simple key transformations, for example removing a
prefix from ``SCRIPT_NAME``, adding to existing values, etc.

Like the WSGI callable, a cleanup callable may also be supplied as a
string to be resolved at runtime.

Built-In Cleanup
================

The built-in cleanup function takes a dict ``d`` and runs
``environ.update(d)``.  This behavior can be augmented with magic
``wfront.*`` keys in your dictionary.  For example::

    { 'HTTPS': 'on',
      'wfront.remove.REMOTE_USER': 'true',
      'wfront.copy.REMOTE_HOST': 'our.remote_host.key',
      'wfront.subtract.HTTP_ACCEPT_ENCODING': 'deflate' }
  
The ``wfront.*`` directives operate on the existing environ values and
take the general form::

    'wfront.<action>.<environ key>' = '<new value>'

- ``wfront.copy.<source key> = <target key>``
    Copy ``environ['<source key']`` to ``environ['<target key>']``::

     { 'wfront.copy.HOST': 'my.host.key' }

- ``wfront.subtract.<key> = 'string'``
    Remove the first occurrence of 'string' in <key>'s value::

    { 'wfront.subtract.SCRIPT_NAME': '/remove/this/prefix' }

- ``wfront.sub.<key> = 'regex' or regular expression object``
    Remove the first occurrence of ``regex`` in <key>'s value::

    { 'wfront.sub.HTTP_ACCEPT_ENCODING': r',?deflate' }

- ``wfront.sprintf.<key> = '%s template'``
    Place <key>'s value in the sprintf-style template.  The first
    occurrence of %s in the template will be replaced with <key>'s
    current value, and the result assigned back to environ

::

    { 'wfront.sprintf.SCRIPT_NAME': '/prepended/%s',
      'wfront.sprintf.PATH_INFO': '%s/appended',
      'wfront.sprintf.sandwich': 'in the %s middle' }

- ``wfront.remove.<key> = unspecified``
    Remove <key> from environ completely::

    { 'wfront.remove.REMOTE_USER': True }

- ``wfront.strip_path = 'prefix'``

    This command takes no <key> argument.  ``prefix`` is removed
    from ``SCRIPT_NAME``, ``PATH_INFO``, and ``REQUEST_URI``.

A less verbose syntax is available by supplying
``cleanup_syntax='shortcut'`` to the WFront constructor. This is not
enabled by default.

- ``{ '=source' : 'target' }``
   Copy

- ``{ '-key' : 'string' }``
   Subtract

- ``{ '~key' : 'regex' }``
   Sub

- ``{ '%key' : 'template' }``
   Sprintf

- ``{ 'key' : None }``
   Remove

- ``{ '-/' : 'prefix' }``
   Strip Path
   

Cookbook
========

Dispatch proxied VirtualHost requests from Apache with confidence:

::

  httpd.conf:
  # Two secure VirtualHosts, each on a separate IP.
  <VirtualHost 127.0.0.1:443>
     ServerName www.example.com
     #...
     RewriteRule ^(/myapp.*)  http://localhost:8001/example.com/$1 [P] [L]
  </VirtualHost>
  <VirtualHost 127.0.0.2:443>
     ServerName www.example.org
     #...
     RewriteRule ^(/myapp.*)  http://localhost:8001/example.org/$1 [P] [L]
  </VirtualHost>

  our-app.py:
  # Link VirtualHosts to 'exampleapp', some WSGI callable 
  map = [ ('www.example.com:https', exampleapp, None),
          ('www.example.org:https', exampleapp, None), ]

  # Let's say we set up our development-mode server to listen on
  # 8000 and 8443.

  router = wfront.by_scheme(map,
                            schemes={'http':(80,8000),'https:':(443,8443)})

  # For development, we're done.  'router' will work as-is.

  # But we need a little glue for the production environment.  When
  # mod_proxy sends requests over, they'll connect to our process as
  # straight HTTP and may not have a host header.  We've added
  # unique path prefixes in the proxy configuration to make precise
  # mapping possible.
  
  # Set up a WFront that translates prefixes to host information.

  proxied = [
    ('::/example.com', router, { 'HTTP_HOST': 'www.example.com',
                                 'HTTPS': 'on',
                                 'SERVER_NAME': 'www.example.com',
                                 'SERVER_PORT': '443',
                                 'wfront.strip_path': '/example.com' }),
    ('::/example.org', router, { 'HTTP_HOST': 'www.example.org',
                                 'HTTPS': 'on',
                                 'SERVER_NAME': 'www.example.org',
                                 'SERVER_PORT': '443',
                                 'wfront.strip_path': '/example.org' }) ]

  if running_in_development_mode:  # e.g.
    front = router
  else:
    # Check each request for the path prefixes we added in the proxy
    # configuration.  When we get one of these, re-write the request
    # to make our process feel just like what the user's user agent
    # has connected to.
    front = wfront.route(proxied, default=front)

Changelog
=========

Version 0.3.0- initial public release.

Notes
=====

Tested with:

- paste.httpserver
- multiserver, a multi-port variant of paste.httpserver
- flup.ajp
- Apache 2.0 mod_proxy, mod_rewrite
- Apache 2.2 mod_proxy, mod_rewrite, mod_proxy_ajp

TODO
====

-  I think there's a string-resolver in setuptools too.
-  Direct support for launching Paste apps.
"""

string_loader = None
try:
    import resolver
    string_loader = lambda s: resolver.resolve(s)
except ImportError:
    try:
        import paste.util.import_string
        string_loader = lambda s: paste.util.import_string.eval_import(s)
    except ImportError:
        def string_loader(s):
            raise ImportError("Can not load %s via introspection: 'resolver' "
                              "and/or 'Paste' are required for "
                              "this feature." % s)
        # or, to fail later:
        #string_loader = lambda s: lambda e,sr: [ (sr('500 Error', []) or
        #                  "Application '%s' could not be loaded" % s) ]

import re, sys

__all__ = ['WFront', 'MacroMap', 'route', 'by_port', 'by_scheme']
__author__ = 'Jason Kirtland'
__version__ = '0.3.1'


def host_portnumber(environ, host_is_proxied=False, **kw):
    """Basic HTTP_HOST parser, ensures that something is present even
    if the header is not present."""

    host = ''

    path = environ.get('REQUEST_URI', None)
    if path is None:
        # It's a shame REQUEST_URI isn't part of the WSGI spec.  It's a useful
        # Apache extension.
        environ['REQUEST_URI'] = path = (environ.get('SCRIPT_NAME', '') +
                                     environ.get('PATH_INFO'))

    # mod_proxy-style forward?
    if 'HTTP_X_FORWARDED_FOR' in environ:
        # Some proxy setups can pass along the original Host.
        if host_is_proxied and 'HTTP_HOST' in environ:
            host = environ['HTTP_HOST']
        # Others pass it in an x-header
        elif 'HTTP_X_FORWARDED_HOST' in environ:
            host = environ['HTTP_X_FORWARDED_HOST']
        # Or default to remote server name if the client didn't supply Host:
        elif 'HTTP_X_FORWARDED_SERVER' in environ:
            host = environ['HTTP_X_FORWARDED_SERVER']
        # Otherwise ignore Host: and default to our server name.
        else:
            host = environ['SERVER_NAME']

        # In a proxy situation, the original request port is only known if
        # there is a Host: or forwarded Host: header AND the request is either
        # on a non-standard port or is http on port 80.  There's no way to
        # distinguish a simply-proxied HTTP and HTTPS connection!
        # Given that, default to 80.  Ignore wsgi.url_scheme until such a time
        # as the WSGI spec makes it clear if this is variable describes the
        # *user's* URL scheme or the application container's URL scheme.  It's
        # safer to assume the latter.
        if host.find(':') == -1: host += ':80'
        return host + ':' + path

    # Not mod_proxy proxied- assume direct connection.
    else:
        host = environ.get('HTTP_HOST', None)
        if host is None:
            host = environ['SERVER_NAME'] + ':' + environ['SERVER_PORT']

        if host.find(':') == -1:
            if (environ.get('HTTPS', '').lower() in ('yes', 'on', '1') or
                    environ.get('wsgi.url_scheme', '') == 'https'):
                host += ':443'
            else:
                host += ':80'

        return host + ':' + path
    
def host_scheme_factory(schemes={}, **kw):
    """Add indirection to HTTP_HOST: allow path expressions to match on the
    connection scheme (e.g. http vs https) without caring about the particular
    port that is listening.
    """
    ports = {}
    for label in schemes:
        if type(schemes[label]) is not tuple:
            port = schemes[label]
            ports[str(port)] = label
        else:
            for port in schemes[label]:
                ports[str(port)] = label

    def resolver(environ):
        host, port, path = host_portnumber(environ, **kw).split(':', 3)
        if port in ports:
            return ':'.join((host, ports[port], path))
        else:
            return ':'.join((host, port, path))

    return resolver
  
def by_port(mapping, **kw):
    return WFront(mapping, host_resolver=host_portnumber, **kw)

route = by_port

def by_scheme(mapping, schemes={'http': (80,), 'https': (443,)}, **kw):
    resolver = host_scheme_factory(schemes, **kw)
    return WFront(mapping, host_resolver=resolver, **kw)
  
def abort404(environ, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return ['No website configured at this address, dude.']

class WFront(object):
    def __init__(self, mapping, default=None, host_resolver=host_portnumber,
               abort404=abort404, cleanup_syntax='verbose', **kw):
        """
        Create WFront middleware with the given mapping.

            front = WFront([('localhost', myapp, None)])

            mapping = [ ('www.example.com', myapp),
                        ('www.example.com:443', sec_app, 'mymodule.cleanup'),
                        ('wap.example.mobi', myapp, {'mode': 'wap'}), ]

            front = WFront(mapping)
            return front(environ, start_response)

        See package documentation for a description of the mapping
        specification.

        'default', if provided, is run if there are no hits in the
        map. Default can be either a app or tuple of app, cleanup.

        By default, the requested host is taken from HTTP_HOST and
        guaranteed to contain a port number.  You can customize this
        behavior by supplying 'host_resolver' as a function that takes the
        environ and returns a string of 'hostname:port:path'

        'abort404' is a WSGI app that will be run if there are no map
        hits and no 'default' is provided.
        """

        self.mapping      = []

        self.host_resolver  = host_resolver
        self.abort404       = callableize(abort404)
        self.cleanup_syntax = cleanup_syntax

        if default:
            if type(default) is not tuple:
                default = (default, None)

            app, cleanup = default
            default = (callableize(app), self._prepare_cleanup(cleanup))

        self.default        = default

        for spec in mapping:
            self.add(*spec)

    def __call__(self, environ, start_response):
        req = self.host_resolver(environ)

        for r, app, cleanup in self.mapping:
            if r.match(req):
                break
        else:
            if self.default:
                app, cleanup = self.default
            else:
                return self.abort404(environ, start_response)

        if not cleanup:
            return app(environ, start_response)
        elif type(cleanup) is dict:
            environ.update(cleanup)
            return app(environ, start_response)
        else:
            return app(*cleanup(environ, start_response))

    def add(self, spec, app, cleanup=None):
        """Add a new mapping.  Spec may be a regex in which case it is
        used as-is, otherwise spec is regex-escaped and converted into a
        host:port:path matcher.
        """
        if not spec:
            regex = re.compile(r'^')
        elif hasattr(spec, 'match'):
            regex = spec
        else:
            sections = map(lambda s, d: ((s is None or s == '')
                                   and d or self._glob(s)),
                     spec.split(':'), ['[^:]+'] * 3)

            regex = re.compile('^%s' % ':'.join(sections))

        self.mapping.append((regex,
                         callableize(app),
                         self._prepare_cleanup(cleanup)))
    

    def _prepare_cleanup(self, cleanup):
        if not cleanup:
            return None
        elif type(cleanup) is dict:
            return self.builtin_cleanup_factory(cleanup,
                                                syntax=self.cleanup_syntax)
        else:
            return callableize(cleanup)

    def dump_mappings(self):
        """Dump the decompiled regex patterns."""
        return [r.pattern for r, _, _ in self.mapping]

    def _glob(self, item):
        r"""
        Convert strings of the form *.example.com into regexes-ready string.

        >>> wf = WFront([])
        >>> wf._glob('*.example.com:80')
        '.*?\\.example\\.com\\:80'
        """
        return re.sub(r'\\\\\*', '*',
                      re.sub(r'(?<!\\)\\\*', '.*?',
                             re.escape(item)))


    def builtin_cleanup_factory(self, data, syntax='verbose'):
        """Given a cleanup dict, determines if this should be straight
        dict.update() or a directed merge.  Returns either a update()-suitable
        dict or a cleanup callable for use at request time."""

        if not data:
            return None
    
        if syntax == 'shortcut':
            copy, subtract, re_subtract, sprintf, remove, replace = \
                self._shortcut_cleanup_parse(data)
        else:
            copy, subtract, re_subtract, sprintf, remove, replace = \
                self._verbose_cleanup_parse(data)

        # If all requests are to overwrite existing environ keys, let
        # dict.update() handle this.
        if len(data) == len(replace):
            return data

        def patch_environ(environ, start_response):
            # Copy environ keys.
            for key, target in copy:
                if key in environ:
                    environ[target] = environ[key]
        
            # Remove first occurance of string in environ value,
            for key, substr in subtract:
                if key in environ:
                    environ[key] = str(environ[key]).replace(substr, '', 1)

            # Remove first occurance of regex in environ value.
            for key, pattern in re_subtract:
                if key in environ:
                    environ[key] = re.sub(pattern, '', str(environ[key]), 1)

            # Insert strings. 
            if sprintf:
                safe = EmptyStringProxy(environ)
                for key, insert in sprintf:
                    if key in environ:
                        environ[key] = environ[key] % safe

            for key in remove:
                environ.pop(key, None)

            environ.update(replace)

            return environ, start_response

        return patch_environ

    def _shortcut_cleanup_parse(self, d):
        expanded = {}
        for key, value in d.items():
            if type(key) not in (str, unicode):
                expanded[key] = value
            elif key == '-/':
                expanded['wfront.strip_path'] = value
            elif value is None:
                expanded['wfront.remove.' + key[1:]] = None
            elif key[0] == '%':
                expanded['wfront.sprintf.' + key[1:]] = value
            elif key[0] == '-':
                expanded['wfront.subtract.' + key[1:]] = value
            elif key[0] == '~':
                expanded['wfront.sub.' + key[1:]] = value
            elif key[0] == '=':
                expanded['wfront.copy.' + key[1:]] = value
            else:
                expanded[key] = value

        return self._verbose_cleanup_parse(expanded)
      
    def _verbose_cleanup_parse(self, d):
        copy, subtract, re_subtract, sprintf, remove, replace = \
            [], [], [], [], [], []

        # Macro: Remove a component from routable URI path keys.
        if 'wfront.strip_path' in d:
            prefix = d.pop('wfront.strip_path')
            d['wfront.subtract.SCRIPT_NAME'] = prefix
            d['wfront.subtract.PATH_INFO'] = prefix
            d['wfront.subtract.REQUEST_URI'] = prefix

        for key, value in d.items():
            if type(key) not in (str, unicode):
                replace.append( (key, value) )
                continue
            elif key.find('wfront.') != 0:
                replace.append( (key, value) )
                continue

            if key.find('.') == key.rfind('.'):
                (_, action), target = key.split('.'), None
            else:
                _, action, target = key.split('.', 3)
      

            if action == 'copy':
                copy.append( (key, value) )
      
            elif action == 'subtract':
                subtract.append( (target, value) )

            elif action == 'sub':
                if hasattr(value, 'match'):
                    re_subtract.append( (target, value) )
                else:
                    re_subtract.append( (target, re.compile(value)) )

            elif action == 'sprintf':
                value = re.sub(r'(?<!%)%s', '%(' + key + ')s', value, 1)
                sprintf.append( (target, value) )

            elif action == 'remove':
                remove.append( target )
      
            else:
                replace.append( (key, value) )
      
        return copy, subtract, re_subtract, sprintf, remove, replace    
    
class MacroMap(list):
    """A route map creation helper.  Can be seeded with a sequence of routing
    tuples or constructed piece-by-piece with add().  Routing specs can
    undergo macro expansion: supply a dict of key/value mappings, and each
    spec will be expanded as it is interned.
    
    >>> mm = MacroMap(macros={'domain':'example.com'})
    >>> mm.add('{domain}:http', 'app')
    >>> mm.add('www.{domain}:http', 'app')
    >>> mm.add('{domain}:https', 'sslapp')
    >>> mm.add('www.{domain}:https', 'sslapp')
    """
    def __init__(self, sequence=None, macros={}):
        self.macros = macros
        if sequence is not None:
            for item in sequence:
                if type(item) is not tuple:
                    raise ValueError(
                        'Mapping sequence must consist of tuples.')
                self.add(*item)

    def add(self, spec, app, data=None):
        self.append( (self.expand(spec), app, data) )

    def expand(self, spec):
        spec = re.sub(r'\{([^}]+)\}', r'%(\1)s', spec)
        return spec % self.macros

def callableize(f):
    # This could be made lazy, but I think it's better to fail early
    # if the string_loader can't find the app.
    if not callable(f):
        f = string_loader(f)
        assert(callable(f))
    return f

class EmptyStringProxy(object):
    """Wrapper for sprintf formating using environ: ignore runtime KeyErrors
    by returning empty string for missing keys."""
    def __init__(self, source):
        self.source = source
    def __getitem__(self, key):
        return self.source.get(key, '')
    def get(self, key, default=None):
        return self[key]
    def __contains__(self, key):
        return True
    def has_key(self, key):
        return True
  

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    import wsgiref.util
    try:
        _test()
    except TypeError:  # ipython
        pass

    environ = {}
    wsgiref.util.setup_testing_defaults(environ)
  
    def start_response(s, h):
        print "Status: %s" % s
    
    def appA(environ, start_response):
        start_response('200 OK', [])
        return ['app A: %s' % environ.get('test.msg', 'No message')]

    def appB(environ, start_response):
        start_response('200 OK', []) 
        return ['app B: %s' % environ.get('test.msg', 'No message')]

    config = \
        [ ('127.0.0.1', appA, { 'test.msg' : '127.0.0.1' } ),
            ('localhost:80', appA, { 'test.msg': 'localhost:80' } ),
            ('localhost::/pony', appA, { 'test.msg': 'any localhost pony' } ),
            # Or list the app by name:
            ('www.example.com', '__main__:appB',
         { 'test.msg': 'www.example.com:' } ),
            ('*.example.net', '__main__:appB',
         { 'test.msg': 'any *.example.net:' } ),
            (':80', appA, { 'test.msg': 'any port 80' } ),
            ('::/pony', appA, { 'test.msg': 'any pony' } ),
            ]

    wf = route(config)

    # Show compiled mappings:
    #wf.dump_mappings()

    def tryit(host='localhost:80', path='/'):
        env = environ.copy()
        env['HTTP_HOST'] = host
        env['PATH_INFO'] = path
        print "HTTP/1.1 GET %s" % path
        print "Host: %s\n" % host
        return wf(env, start_response)

    # tryit('127.0.0.1')
    # tryit('127.0.0.1', '/pony')
    # tryit('localhost:443', '/pony')
    # tryit('www.example.com:443', '/pony')
    # tryit('www.example.com:80', '/')

    templated = MacroMap([('www.{domain}:https', lambda e,s:['1']),
                          ('{domain}', lambda e,s:['2']),
                          ('mirror.{domain}:http', lambda e,s:['3'])],
                         macros={'domain': 'example.org'})

    wfi = by_scheme(templated,
                    schemes={'http': (80, 8080), 'https': (443, 8443),})
    #wfi.dump_mappings()
