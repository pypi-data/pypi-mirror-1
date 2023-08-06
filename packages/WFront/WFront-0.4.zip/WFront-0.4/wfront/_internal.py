"""WSGI request routing.

:copyright: the WFront authors and developers, see AUTHORS.
:license: MIT, see LICENSE for more details.

"""
import re


try:
    callable
except NameError:
    def callable(fn):
        return hasattr(fn, '__call__')

def _abort404(environ, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return ['No website configured at this address, dude.']

def _callableize(fn):
    # This could be made lazy, but I think it's better to fail early
    # if the string_loader can't find the app.
    if not callable(fn):
        fn = _string_loader(fn)
        assert(callable(fn))
    return fn

def _glob(item):
    """
    Convert strings of the form *.example.com into ``re`` syntax.

      >>> _glob('*.example.com:80')
      '.*?\\.example\\.com\\:80'

    """
    if item is None:
        return ''
    return re.sub(r'\\\\\*', '*',
                  re.sub(r'(?<!\\)\\\*', '.*?',
                         re.escape(item)))


def _import(module_name):
    local_name = module_name.split('.')[-1]
    return __import__(module_name, {}, {}, local_name)

def _import_some(dotted_path):
    """Import as much of dotted.path as possible, returning module and
    remainder."""
    steps = list(dotted_path.split('.'))
    modname = [steps.pop(0)]
    mod = _import(modname[0])
    while steps:
        try:
            mod = _import('.'.join(modname + steps[:1]))
        except ImportError:
            break
        else:
            modname.append(steps.pop(0))
    return mod, '.'.join(steps)

def _string_loader(string):
    """module.member.member or module.module:evaled.in.module"""

    if ':' not in string:
        mod, expr = _import_some(string)
    else:
        modname, expr = string.split(':', 1)
        mod = _import(modname)
    if expr:
        return eval(expr, mod.__dict__)
    else:
        return mod


class _pyformat_proxy(object):
    """Wrapper for lax ``%`` formating using environ.

    Ignores runtime KeyErrors by returning empty string for missing keys.

    """
    __slots__ = 'source',

    # FIXME:jek drop most of these methods
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


def _demote_pathinfo(environ, path):
    # environ[PATH_INFO] *must* start with path!
    environ['PATH_INFO'] = environ['PATH_INFO'][len(path):]
    environ['SCRIPT_NAME'] += path

def _copy_function(fn, name=None, doc=None):
    name = name or fn.__name__
    clone = type(_copy_function)(fn.func_code, fn.func_globals, name,
                                 fn.func_defaults, fn.func_closure)
    if doc:
        clone.__doc__ = doc
    return clone

def _pair_iterator(obj):
    """Return a (key, value) iterator for a dict-like or sequence of tuples.

    Implements an optimized version of the dict.update() definition of
    "dict-like".

    """
    if hasattr(obj, 'iteritems'):
        return obj.iteritems()
    elif hasattr(obj, 'items'):
        return iter(obj.items())
    elif hasattr(obj, 'keys'):
        return ((key, obj[key]) for key in obj.keys())
    elif hasattr(obj, 'next') or hasattr(obj, '__next__'):
        return obj
    else:
        return ((key, value) for key, value in obj)
