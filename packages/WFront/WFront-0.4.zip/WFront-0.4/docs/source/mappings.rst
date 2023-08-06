Mappings
********

.. testsetup::

  from examples import Symbol
  app = Symbol('app')
  app1 = Symbol('app1')
  app2 = Symbol('app2')

WFront is driven by a routing map or *mapping*.  The mapping is a
sequence of 1 or more 3-tuples:

  (**path specification**, **wsgi callable**, **filter**)

For example:

.. testcode::

  mapping = [
      ('www.example.com', app1, None),
      ('www.example.com:3000', app2, {'environ_key':'value'})
  ]


Path Specifications
-------------------

Path specifications (or path specs) are compared to the WSGI environ's
requested **hostname**, **port** and **path**.  A path spec is a
colon-separated string, and sections may use ``*`` wildcard matching.
Empty or missing sections match anything.

::

  www.example.com
  www.example.com:80
  www.example.com:80:/some/path
  *.example.com::/some/path
  :80
  ::/some/path

The incoming ``Host:`` header and ``environ['PATH_INFO']`` supply the match
data by default.


WSGI Callables
--------------

The WSGI application may be supplied either as a callable or a string.

Strings are evaluated and are expected to resolve to a callable.  The
evaluation syntax is similar to that of several popular Python string
resolvers.

**Dotted Path**

Format:
  ``wsgiref.simple_server.demo_app``

Imports modules as needed, doing a getattr() on each to reach a target.  The above is identical to:

.. testcode::

  import wsgiref.simple_server
  wsgiref.simple_server.demo_app

.. testcode:: :hide:

  from wfront import _internal
  _internal._string_loader('wsgiref.simple_server.demo_app')

**Import and Eval**

Format:
  ``os:environ["PATH"]``

Imports the dotted module path before the colon, and evals() the portion after the colon in that module's namespace.  The above is identical to:

.. testcode::

  import os
  os.environ["PATH"]

.. testcode:: :hide:

  _internal._string_loader('os:environ["PATH"]')


Filters
-------

Filters have the opportunity to fine-tune the ``environ`` before the WSGI
callable executes and/or rewrite the WSGI response.  Filters may take several
forms.

``None``

  No filtering takes place.

A ``dict``

  WFront will ``environ.update(your_dict)`` before invoking the WSGI
  callable.

A ``dict`` with rewriting directives

  You may request simple environ transformations, for example removing a
  prefix from ``SCRIPT_NAME``, trimming off part ``PATH_INFO``, adding to
  existing values, etc.  See :ref:`filter`.  The rewriting functionality is
  also available as an independent WSGI middleware.

A callable

  The most general option is a callable that wraps the WSGI application, of
  the form:

  .. function:: filter(app, environ, start_response) -> response

  The filter is responsible for producing the WSGI response, usually through
  ``return app(environ, start_response)``.  Like the WSGI application
  callable, a filter callable may also be supplied as a string to be resolved
  at runtime.

Mapping Helpers
---------------

Some mappings can be made briefer and more idiomatic with one of the built-in
mapping helpers.  These are simple extensions of :class:`list` that build
mapping 3-tuples in different ways.

.. currentmodule:: wfront

.. testsetup::

  from wfront import MacroMap, PathMap

MacroMap
^^^^^^^^

.. autoclass:: wfront.MacroMap
   :show-inheritance:
   :members:

PathMap
^^^^^^^

.. autoclass:: wfront.PathMap
   :show-inheritance:
   :members:

   .. automethod:: __init__
