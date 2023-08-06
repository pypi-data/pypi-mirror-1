"""
======
WFront
======

A WSGI front-door dispatcher, virtual host router and environ
manipulation swiss-army knife.

WFront is a top-level request dispatcher, directing requests based on
the requested "Virtual Host", listening port, URL path, or any
combination.

WFront can be used to:

 * host multiple WSGI-powered domains in a single process
 * emulate a mod_proxy, SCGI/FastCGI/AJP, mod_wsgi, or mod_python WSGI
   setup under a simple development mode WSGI server,
 * simplify development and testing of complex, multi-server cluster
   environments
 * or just perform simple path-based request dispatching

Mapping HTTP/1.0 requests to HTTP/1.1 Host:-style requests is supported
and is very flexible.  WFront includes an environ manipulation toolkit
that allows for additions to and transformations of server-provided
environ data to be performed on each request.

The `development version
<http://www.bitbucket.org/jek/wfront/get/tip.tgz#WFront==dev>`_ of
WFront can be installed via ``easy_install WFront==dev`` or from the
`mercurial repository <http://www.bitbucket.org/jek/wfront>`_.

"""


try:
    from setuptools import setup
    extra_setup = dict(
        zip_safe = True,
        extras_require = {'multiserver' : ['Paste>=1.1', 'setuptools'] },
        tests_require=['nose'],
        # for tests, prefer just 'nosetests tests'
        test_suite='nose.collector',
        )
except ImportError:
    from distutils import setup
    extra_setup = {}

setup(name="WFront",
      version="0.4",
      packages=['wfront'],
      author="Jason Kirtland",
      author_email="jek@discorporate.us",
      description='A WSGI front-door dispatcher.',
      keywords="wsgi web http vhost virtualhost proxy mod_proxy dispatcher",
      long_description=__doc__,
      license='MIT License',
      url='http://discorporate.us/projects/WFront/',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.4',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
                   'Topic :: Software Development :: Libraries'],
      **extra_setup
      )
