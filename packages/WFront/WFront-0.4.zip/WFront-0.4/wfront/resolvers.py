_ssl_flags = set(('https', 'on', 'yes', '1'))


class RouteResolver(object):
    """Extracts 'host:portnumber:path' from an environ."""

    proxied_host_is_accurate = True

    def __call__(self, environ):
## default_resolver ##
        path = environ.get('REQUEST_URI', None)
        if path is None:
            path = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO')

        # mod_proxy-style forward?
        if 'HTTP_X_FORWARDED_FOR' in environ:
            # Some pass it in an x-header
            if 'HTTP_X_FORWARDED_HOST' in environ:
                host = environ['HTTP_X_FORWARDED_HOST']
            # some others pass along the original Host:
            elif self.proxied_host_is_accurate and 'HTTP_HOST' in environ:
                host = environ['HTTP_HOST']
            # Or, default to remote server name if the client didn't
            # supply Host:
            elif 'HTTP_X_FORWARDED_SERVER' in environ:
                host = environ['HTTP_X_FORWARDED_SERVER']
            # Otherwise ignore Host: and default to our server name.
            else:
                host = environ['SERVER_NAME']
            # In a proxy situation, the original request port is only
            # known if there is a Host: or forwarded Host: header AND
            # the request is either on a non-standard port or is http
            # on port 80.  There's no way to distinguish a
            # simply-proxied HTTP and HTTPS connection!  Given that,
            # default to 80.  Ignore wsgi.url_scheme until such a time
            # as the WSGI spec makes it clear if this is variable
            # describes the *user's* URL scheme or the application
            # container's URL scheme.  It's safer to assume the
            # latter.
            if ':' not in host:
                host += ':' + environ.get('HTTP_X_FORWARDED_PORT', '80')
            return host + ':' + path
        # Not mod_proxy-style proxied- assume direct connection.
        else:
            host = environ.get('HTTP_HOST', None)
            if host is None:
                host = environ['SERVER_NAME'] + ':' + environ['SERVER_PORT']
            elif ':' not in host:
                ssl = environ.get('HTTPS', environ['wsgi.url_scheme']).lower()
                if ssl in _ssl_flags:
                    host += ':443'
                else:
                    host += ':80'
            return host + ':' + path
## default_resolver ##

default_resolver = RouteResolver()
default_resolver.__name__ = 'default_resolver'
modproxy_resolver = RouteResolver()
modproxy_resolver.proxied_host_is_accurate = False
modproxy_resolver.__name__ = 'modproxy_resolver'
modproxy_resolver.__doc__ += """\

This resolver will attempt to use X-Forwarded-Host if present and will
ignore any Host: header offered by the server.

"""

class LogicalRouteResolver(RouteResolver):
    """Resolve ports as logical names (e.g. http) rather than raw numbers."""

    def __init__(self, schemes, proxied_host_is_accurate=None):
        """Construct a LogicalRouteResolver.

        :param schemes: a mapping of labels such as 'http' to
          sequences of port numbers.
        :param proxied_host_is_accurate: if supplied and False, Host
          resolution will occur as for
          :func:`wfront.modproxy_resolver`.

        """
        self.schemes = schemes
        self.by_port = by_port = {}
        for label, ports in schemes.items():
            if not isinstance(ports, (tuple, list)):
                by_port[str(ports)] = label
            else:
                for port in ports:
                    by_port[str(port)] = label
        if proxied_host_is_accurate is not None:
            self.proxied_host_is_accurate = proxied_host_is_accurate

    def __call__(self, environ):
        resolved = RouteResolver.__call__(self, environ)
        host, port, path = resolved.split(':', 2)
        label = self.by_port.get(port, port)
        return host + ':' + port + ':' + path
