"""A WSGI front-door virtual host dispatcher and server adapter toolkit.

:copyright: the WFront authors and developers, see AUTHORS.
:license: MIT, see LICENSE for more details.

"""
from base import (
    MacroMap,
    PathMap,
    WFront,
    by_scheme,
    echo_app,
    route,
    )
from resolvers import default_resolver, modproxy_resolver
from rewriter import EnvironRewriter


__version__ = '0.4'
