#######
Routing
#######

.. currentmodule:: wfront

wfront.router
*************

.. autofunction:: route

Routing by URL Scheme
*********************

.. autofunction:: by_scheme

Custom Routers
**************

The base implementation can be extended for custom functionality.

.. autoclass:: WFront
   :members:
   :undoc-members:

   .. automethod:: __init__


Virtual Host Resolution
***********************

.. autofunction:: default_resolver

.. autofunction:: modproxy_resolver


In many cases, this function will 'just work' and retrieve the correct
'hostname' and 'path' from the environ with no fuss.  If it is not
working for your web server and/or WSGI container, the implementation
is listed below.

.. delimited-include:: ../../wfront/resolvers.py
   :delim-id: default_resolver
   :literal:
