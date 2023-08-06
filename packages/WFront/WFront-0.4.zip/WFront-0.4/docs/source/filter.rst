.. _filter:

.. currentmodule:: wfront.rewriter

Built-In Cleanup Filter
***********************

The built-in filter function takes a dict ``d`` and runs
``environ.update(d)``.  This behavior can be augmented with magic ``wfront.*``
directives in your dictionary.  For example::

    { 'HTTPS': 'on',
      'wfront.remove.REMOTE_USER': 'true',
      'wfront.copy.REMOTE_HOST': 'our.remote_host.key',
      'wfront.subtract.HTTP_ACCEPT_ENCODING': 'deflate' }

The directives are consumed by the filter function and will not be placed into
the final ``environ``.

Rewrite Directives
------------------

The ``wfront.*`` directives operate on the existing environ values and
take the general form:

  ``'wfront.<directive>.<environ key>' = '<new value>'``

copy
^^^^

Format:
  ``wfront.copy.<source key> = <target key>``

Copies ``environ['<source key>']`` to ``environ['<target key>']``::

  { 'wfront.copy.HOST': 'my.host.key' }

subtract
^^^^^^^^

Format:
  ``wfront.subtract.<key> = 'string'``

Removes the first occurrence of 'string' in ``<key>``'s value::

{ 'wfront.subtract.SCRIPT_NAME': '/remove/this/prefix' }

sub
^^^

Format:
  ``wfront.sub.<key> = 'regex as a string'``

  ``wfront.sub.<key> = re.compile('regex object')``

Removes the first occurrence of ``regex`` in ``<key>``'s value::

  { 'wfront.sub.HTTP_ACCEPT_ENCODING': r',?deflate' }

sprintf
^^^^^^^

Format:
  ``wfront.sprintf.<key> = '%s template'``

Places ``<key>``'s value in the sprintf-style template.  The first occurrence
of %s in the template will be replaced with ``<key>``'s current value, and the
result assigned back to environ::

  { 'wfront.sprintf.SCRIPT_NAME': '/prepended/%s',
    'wfront.sprintf.PATH_INFO': '%s/appended',
    'wfront.sprintf.sandwich': 'in the %s middle' }

You can insert the values of other environ keys with named formats::

  { 'wfront.sprintf.foo': 'bar is %(bar)s' }

setdefault
^^^^^^^^^^

Format:
  ``wfront.setdefault.<key> = 'value'``

  ``wfront.setdefault.<key> = '%(other-key)s'``

Sets ``<key>`` to ``value`` only if ``<key>`` is not present in the environ or
is present with a value of ``''``, an empty string::

  { 'wfront.setdefault.HTTP_HOST: 'www.example.com' }

``value`` may contain sprintf-style substitutions to insert values from other
environ keys::

  { 'wfront.setdefault.REQUEST_URI': '%(SCRIPT_NAME)s%(PATH_INFO)s' }

remove
^^^^^^

Format:
  ``wfront.remove.<key> = unspecified``

Removes ``<key>`` from environ completely.  The value is ignored::

  { 'wfront.remove.REMOTE_USER': True }

strip_path
^^^^^^^^^^

Format:
  ``wfront.strip_path = 'prefix'``

This directive takes no ``<key>`` argument.  ``prefix`` is removed from
``SCRIPT_NAME``, ``PATH_INFO``, and ``REQUEST_URI``::

  { 'wfront.strip_path': '/bogus/' }

reset_host
^^^^^^^^^^

Format:
  ``wfront.reset_host = unspecified``

This command takes no ``<key>`` argument and ignores the value.  Sets the
``Host:`` header to match the determination made by WFront's Host detection
heuristics.

Will use ``wfront_match`` if present in the
``environ['wsgiorg.routing_args']`` collection, otherwise the ``Host:`` will
be determined using the current state of the environ.

::

  { 'wfront.reset_host: '' }


Shorthand
---------

A less verbose syntax is available by supplying ``cleanup_syntax='shortcut'``
to the WFront constructor. This is not enabled by default.

``=source: target``
  Alias for ``wfront.copy.<source> = <target>``

``-key: string``
  Alias for ``wfront.subtract.<key> = <string>``

``~key: regex``
  Alias for ``wfront.sub.<key> = <regex>``

``%key: template``
  Alias for ``wfront.sprintf.<key> = <template>``

``key: None``
  Alias for ``wfront.remove.<key> = True``

``-/: prefix``
  Alias for ``wfront.strip_path = <prefix>``

``>host: ignored``
  Alias for ``wfront.reset_host``.  The value is ignored.

Middleware
----------

The rewrite rules can be used standalone as WSGI middleware::

  >>> from wfront import EnvironRewriter, echo_app as my_app
  >>> rewriter = EnvironRewriter(HTTPS='on')
  >>> my_app = rewriter.as_middleware_for(my_app)

.. autoclass:: EnvironRewriter

   .. attribute:: route_resolver

      A route resolving callable.  Defaults to
      :func:`~wfront.default_resolver`.  Used by the ``reset_host``
      rewrite directive.  May be freely reassigned on
      :class:`EnvironRewriter` instances for other behavior.

   .. automethod:: __init__
   .. automethod:: rewrite
   .. automethod:: as_filter
   .. automethod:: as_middleware_for
