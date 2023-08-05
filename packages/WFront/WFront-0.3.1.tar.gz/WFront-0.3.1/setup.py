#!/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

import sys

if sys.version < '2.3':
    print "Python 2.3 or higher is required."
    sys.exit(1)

setup(name = "WFront",
      version = "0.3.1",
      packages = ['wfront'],
      zip_safe = True,

      extras_require = {'StringLoading' : 'Resolver',
                        'StringLoading' : 'Paste'},
      
      #test_suite='tests.suite',

      author = "Jason Kirtland",
      author_email = "jek@discorporate.us",
      description = 'A WSGI front-door dispatcher.',
      keywords="wsgi web http webapps vhost virtualhost proxy mod_proxy url dispatcher",

      long_description = """
      WFront is a simple top-level request dispatcher, directing requests
      based on "Virtual Host".  WFront can be used to host multiple
      WSGI-powered domains in a single process, emulate a mod_proxy,
      SCGI/FastCGI/AJP or mod_python WSGI setup for development, or any other
      composition where operating at the host-level is desired.  Mapping
      HTTP/1.0 requests to HTTP/1.1 Host:-style requests is supported and is
      very flexible.
      """,

      license = 'MIT License',
      url='http://discorporate.us/jek/projects/wfront/',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
                   'Topic :: Software Development :: Libraries']
)
