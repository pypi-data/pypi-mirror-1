"""Declarative WSGI environ manipulation middleware and filters.

:copyright: the WFront authors and developers, see AUTHORS.
:license: MIT, see LICENSE for more details.

"""
from collections import deque
from itertools import chain
import re
from resolvers import default_resolver
from _internal import _pyformat_proxy, _pair_iterator


class EnvironRewriter(object):
    """A WSGI environ tweaker and rewriter."""

    route_resolver = default_resolver

    def __init__(self, *iterable, **rules):
        """Construct a rewriter.

        :param \*iterable: optional, a single sequence of key/value pairs.
        :param \*\*rules: optional, rules as keyword arguments.

        This constructor acts like the Python ``dict`` constructor.

        """
        for attr in ('copy', 'subtract', 're_subtract', 'sprintf',
                     'remove', 'replace', 'setdefault'):
            setattr(self, attr, [])
        self.reset_host = False
        if iterable:
            if len(iterable) != 1:
                raise TypeError(
                    "%s takes at most one non-keyword argument (%s given)" %
                    type(self).__name__, len(iterable))
            self._configure_from_pairs(chain(_pair_iterator(iterable[0]),
                                             _pair_iterator(rules)))
        else:
            self._configure_from_pairs(rules)

    def _configure_from_pairs(self, pairs):
        pairs = deque(_pair_iterator(pairs))
        while pairs:
            key, value = pairs.popleft()

            # Macro: Remove a component from routable URI path keys.
            if key == 'wfront.strip_path':
                pairs.appendleft(('wfront.subtract.SCRIPT_NAME', value))
                pairs.appendleft(('wfront.subtract.PATH_INFO', value))
                pairs.appendleft(('wfront.subtract.REQUEST_URI', value))
                continue
            elif not isinstance(key, basestring) or key[:7] != 'wfront.':
                self.replace.append((key, value))
                continue

            if key.count('.') == 1:
                action = key[7:]
                target = None
            else:
                _, action, target = key.split('.', 2)

            if action in ('copy', 'subtract', 'setdefault', 'replace'):
                getattr(self, action).append((target, value))
            elif action == 'sub':
                if not hasattr(value, 'match'):
                    value = re.compile(value)
                self.re_subtract.append((target, value))
            elif action == 'sprintf':
                value = re.sub(r'(?<!%)%s', '%(' + target + ')s', value, 1)
                self.sprintf.append((target, value))
            elif action == 'remove':
                self.remove.append(target)
            elif action == 'reset_host':
                self.reset_host = True
            else:
                raise NotImplementedError(action)
        return self

    def rewrite(self, environ):
        """Applies rules to *environ*, updating it in place."""
        # Copy environ keys.
        for key, target in self.copy:
            if key in environ:
                environ[target] = environ[key]

        # Remove first occurance of string in environ value
        for key, substr in self.subtract:
            if key in environ:
                environ[key] = str(environ[key]).replace(substr, '', 1)

        # Remove first occurance of regex in environ value.
        for key, pattern in self.re_subtract:
            if key in environ:
                environ[key] = re.sub(pattern, '', str(environ[key]), 1)

        if self.sprintf or self.setdefault:
            safe = _pyformat_proxy(environ)
            # Insert strings.
            for key, insert in self.sprintf:
                environ[key] = insert % safe
            # Set default values
            for key, default in self.setdefault:
                if not environ.get(key, False):
                    environ[key] = default % safe

        for key in self.remove:
            environ.pop(key, None)

        if self.replace:
            environ.update(self.replace)

        if self.reset_host:
            try:
                resolved = environ['wsgiorg.routing_args'][1]['wfront_match']
            except (KeyError, IndexError):
                resolved = self.route_resolver(environ)
            host, port, _ = resolved.split(':', 2)
            # ignoring https://host:80/ and http://host:443/ edge cases.
            if port == '80' or port == '443':
                environ['HTTP_HOST'] = host
            else:
                environ['HTTP_HOST'] = host + ':' + port

    def as_filter(self, app, environ, start_response):
        """Act as a WFront filter."""
        self.rewrite(environ)
        return app(environ, start_response)

    def as_middleware_for(self, app):
        """Act as a middleware wrapping *app*."""
        def filtered_app(environ, start_response):
            return self.as_filter(app, environ, start_response)
        return filtered_app

def expand_shorthand(pairs):
    expanded = []
    for key, value in _pair_iterator(pairs):
        if not isinstance(key, basestring):
            expanded.append((key, value))
        elif key == '-/':
            expanded.append(('wfront.strip_path', value))
        elif key == '>host':
            expanded.append(('wfront.reset_host', value))
        elif value is None:
            expanded.append(('wfront.remove.' + key, value))
        elif key[0] == '%':
            expanded.append(('wfront.sprintf.' + key[1:], value))
        elif key[0] == '-':
            expanded.append(('wfront.subtract.' + key[1:], value))
        elif key[0] == '~':
            expanded.append(('wfront.sub.' + key[1:], value))
        elif key[0] == '=':
            expanded.append(('wfront.copy.' + key[1:], value))
        elif key[:3] == '||=':
            expanded.append(('wfront.setdefault.' + key[3:], value))
        else:
            expanded.append((key, value))
    return expanded
