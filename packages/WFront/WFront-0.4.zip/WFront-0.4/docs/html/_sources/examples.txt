########
Examples
########

Here are some collected recipes and tips for integrating WSGI apps
with various front-end web servers and proxies.

Apache mod_proxy
****************

.. automodule:: examples.apache.mod_proxy


Pound
*****

.. automodule:: examples.pound

.. _running-examples:


Stunnel
*******

``stunnel`` can route HTTPS connections to a back-end WSGI server
quite successfully.  The ``stunnel`` connection is transparent and does
not change the HTTP headers in any fashion, so the Host: header (if
present) is reliable.

However this transparency makes HTTPS detection difficult.  Your WSGI
server will most likely set ``environ['REMOTE_ADDR']`` to the IP
address of the host running ``stunnel``.  A possible approach would be
a filter or WSGI middleware that inspects that address at runtime, and
sets ``wsgi.url_scheme`` appropriately.  This type of conditional
re-writing is currently outside the scope of WFront's built-in
capabilities and would require custom code.


Other Proxies and Front-End Servers
***********************************

Have experience with another tool?  Write-ups and examples gladly accepted.


Running Examples
****************

.. automodule:: examples





