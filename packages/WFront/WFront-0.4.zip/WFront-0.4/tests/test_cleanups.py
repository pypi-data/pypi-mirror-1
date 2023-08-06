import copy
import re
from nose.tools import eq_
from wfront import WFront, rewriter, modproxy_resolver


def apply_rewrite(r, data):
    clone = copy.copy(data)
    r.rewrite(clone)
    return clone

def test_copy():
    spec   = { 'wfront.copy.A': 'B' }
    raw    = { 'A': 'hi' }
    cooked = { 'B': 'hi', 'A': 'hi' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_setdefault1():
    spec   = { 'wfront.setdefault.A': 'foo' }
    raw    = { 'A': 'bar' }
    cooked = { 'A': 'bar' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_setdefault2():
    spec   = { 'wfront.setdefault.A': 'foo' }
    raw    = {}
    cooked = { 'A': 'foo' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_setdefault3():
    spec   = { 'wfront.setdefault.A': 'foo' }
    raw    = { 'A': '' }
    cooked = { 'A': 'foo' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_setdefault4():
    spec   = { 'wfront.setdefault.A': '%(B)s' }
    raw    = { 'A': '', 'B': 'foo' }
    cooked = { 'A': 'foo', 'B': 'foo' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_setdefault5():
    spec   = { 'wfront.setdefault.A': '%(B)s' }
    raw    = {}
    cooked = { 'A': '' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_subtract1():
    spec   = { 'wfront.subtract.A': 'foo' }
    raw    = { 'A': 'foobarbazquux' }
    cooked = { 'A': 'barbazquux' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_subtract2():
    spec   = { 'wfront.subtract.A': 'bar' }
    raw    = { 'A': 'foobarbazquuxfoobarbazquux' }
    cooked = { 'A': 'foobazquuxfoobarbazquux' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_sub1():
    spec   = { 'wfront.sub.A': r'[Qq]uux' }
    raw    = { 'A': 'foobarbazquux' }
    cooked = { 'A': 'foobarbaz' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_sub2():
    spec   = { 'wfront.sub.A': r'quu+x' }
    raw    = { 'A': 'foobarbazquuxquuux' }
    cooked = { 'A': 'foobarbazquuux' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_sub3():
    spec   = { 'wfront.sub.A': re.compile(r'[Qq]uux') }
    raw    = { 'A': 'foobarbazquux' }
    cooked = { 'A': 'foobarbaz' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_sub4():
    spec   = { 'wfront.sub.A': re.compile(r'quu+x') }
    raw    = { 'A': 'foobarbazquuxquuux' }
    cooked = { 'A': 'foobarbazquuux' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_sprintf1():
    spec   = { 'wfront.sprintf.A': '%s_append' }
    raw    = { 'A': 'foo' }
    cooked = { 'A': 'foo_append' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_sprintf2():
    spec   = { 'wfront.sprintf.A': '%(A)s_append' }
    raw    = { 'A': 'foo' }
    cooked = { 'A': 'foo_append' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_sprintf3():
    spec   = { 'wfront.sprintf.A': '%(B)s_append' }
    raw    = { 'A': 'foo', 'B': 'bar' }
    cooked = { 'A': 'bar_append', 'B': 'bar' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_sprintf4():
    spec   = { 'wfront.sprintf.A': '%s%(B)s' }
    raw    = { 'A': 'foo', 'B': 'bar' }
    cooked = { 'A': 'foobar', 'B': 'bar' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_sprintf5():
    spec   = { 'wfront.sprintf.A': '%(bogus)s' }
    raw    = { 'A': 'foo' }
    cooked = { 'A': '' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_sprintf6():
    spec   = { 'wfront.sprintf.A': '%(B)s_append' }
    raw    = { 'B': 'bar' }
    cooked = { 'A': 'bar_append', 'B': 'bar' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_sprintf7():
    spec   = { 'wfront.sprintf.A': '%(B)s_append' }
    raw    = { }
    cooked = { 'A': '_append' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_remove1():
    spec   = { 'wfront.remove.A': '' }
    raw    = { 'A': 'foo' }
    cooked = {  }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_remove2():
    spec   = { 'wfront.remove.B': '' }
    raw    = { 'A': 'foo' }
    cooked = { 'A': 'foo' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_replace1():
    spec   = { 'A': 'borg' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert type(cleaner) is not dict

    cleaner2 = WFront([])._builtin_cleanup_factory(spec)
    assert type(cleaner2) is dict

def test_replace2():
    spec   = { 'A': 'borg', 'wfront.replace.B': 'xyz' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert type(cleaner) is not dict

    cleaner2 = WFront([])._builtin_cleanup_factory(spec)
    assert type(cleaner2) is dict

def test_replace3():
    spec   = { 'A': 'borg', 'wfront.remove.B': '' }

    cleaner = rewriter.EnvironRewriter(spec)
    assert type(cleaner) is not dict

    cleaner2 = WFront([])._builtin_cleanup_factory(spec)
    assert type(cleaner2) is not dict

def test_strip_path1():
    spec   = { 'wfront.strip_path': '/pony' }
    raw    = { 'PATH_INFO': '/pony/powered',
               'SCRIPT_NAME': '/pony/powered',
               'REQUEST_URI': '/pony/powered',
               'foo': 'bar'}
    cooked = { 'PATH_INFO': '/powered',
               'SCRIPT_NAME':'/powered',
               'REQUEST_URI': '/powered',
               'foo': 'bar'}

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_strip_path2():
    spec   = { 'wfront.strip_path': '/pony' }
    raw    = { 'PATH_INFO': '/unicorn/powered',
               'SCRIPT_NAME': '/pony/powered',
               'REQUEST_URI': '/pony/powered',
               'foo': 'bar'}
    cooked = { 'PATH_INFO': '/unicorn/powered',
               'SCRIPT_NAME':'/powered',
               'REQUEST_URI': '/powered',
               'foo': 'bar'}

    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked
    assert apply_rewrite(cleaner, cooked) == cooked

def test_reset_host1():
    spec   = { 'wfront.reset_host': '' }
    raw    = { 'SERVER_NAME': 'server',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'wsgi.url_scheme': 'http'}
    cooked = { 'HTTP_HOST': 'server',
               'SERVER_NAME': 'server',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'wsgi.url_scheme': 'http'}
    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_reset_host2():
    spec   = { 'wfront.reset_host': '' }
    raw    = { 'HTTP_HOST': 'default_is_trusted',
               'SERVER_NAME': 'server',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'wsgi.url_scheme': 'http'}
    cooked = { 'HTTP_HOST': 'default_is_trusted',
               'SERVER_NAME': 'server',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'wsgi.url_scheme': 'http'}
    cleaner = rewriter.EnvironRewriter(spec)
    assert apply_rewrite(cleaner, raw) == cooked

def test_reset_host3():
    spec   = { 'wfront.reset_host': '' }
    raw    = { 'HTTP_HOST': 'overwritten',
               'HTTP_X_FORWARDED_FOR': 'somebody',
               'SERVER_NAME': 'server',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'wsgi.url_scheme': 'http'}
    cooked = { 'HTTP_HOST': 'server',
               'HTTP_X_FORWARDED_FOR': 'somebody',
               'SERVER_NAME': 'server',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'wsgi.url_scheme': 'http'}
    cleaner = rewriter.EnvironRewriter(spec)
    cleaner.route_resolver = modproxy_resolver

    assert apply_rewrite(cleaner, raw) == cooked

def test_shortcuts():
    spec = {
        'A' : '1',
        '-B': '2',
        '~C': '3',
        '~D': re.compile('4'),
        '%E': '5',
        '=F': '6',
        '||=G': '7',
        'H': None,
        '-/': '9',
        }
    cooked = {
        'A' : '1',
        'wfront.subtract.B': '2',
        'wfront.sub.C': '3',
        'wfront.sub.D': re.compile('4'),
        'wfront.sprintf.E': '5',
        'wfront.copy.F': '6',
        'wfront.setdefault.G': '7',
        'wfront.remove.H': None,
        'wfront.strip_path': '9',
        }

    expanded = rewriter.expand_shorthand(spec)
    eq_(dict(expanded), cooked)
    assert dict(expanded) == cooked
