"""A multi-port, multi-interface WSGI server.

**Undocumented, unsupported.** This may be replaced with a spiffier
  version based on Spawning.

A `MultiServer` is a composition of one or more Paste `httpserver`s,
one per port.  All requests on all ports are run through a single
WSGI callable.

Basic Usage
===========
::
    serve(my_app, 8000)
    serve(my_app, (8000, 8001, 8002))
    serve(my_app, [ 8000, ('localhost', 8443 {'ssl': True}) ])

If you have a recent (possibly svn) version of Paste, automatic
"development mode" SSL certificate generation is supported: just
supply `'ssl':True` with the port to bind.

Caveats
=======

This is not a production-quality server.  But it is pretty spiffy
for development.

paste.httpserver supports a 'serve one request' mode; MultiServer currently
does not.

There's no 'paster serve' type script at this point.

Paste 1.0 has some httpserver quirks.  There are patches in svn to
smooth them over, and the code here should run with either 1.0 or svn.
When Paste releases a post 1.0, I'll probably require that version and
pull out the threadpool manipulation etc. from here.

:copyright: the WFront authors and developers, see AUTHORS.
:license: MIT, see LICENSE for more details.

"""
from threading import Thread
from pkg_resources import require
require('Paste >= 1.1')
import sys, inspect, atexit, time, paste.httpserver

__all__ = ['serve', 'MultiServer']
__author__ = 'Jason Kirtland'
__version__ = 0.2

def serve(app, ports, host=None, start_loop=True, **kw):
    """
  serve(app, 8000)
  serve(app, 8000, host='localhost')
  serve(app, (8000, 8001), host='localhost')

  serve(app, [ 8000,
               ('secure.localhost', '8443', { 'ssl_pem': 'secure.pem' } ) ])


  "Anonymous" ports will be bound to all interfaces.  If `host` is
  provided, anonymous ports will bind to that instead.

  You can mix and match bind interfaces with the full bind syntax:

     [ ('IP or hostname', portnum), ... ]
     or
     [ ('IP or hostname', portnum, { server options }), ... ]
     
    """

    httpd = MultiServer(app, ports, host, **kw)

    if start_loop:      
        httpd.serve_forever()
    else:
        return httpd

class MultiServer(object):
    def __init__(self, app, ports, host=None, quiet=False, **kw):
        self.servers, self.threads, self.startup = [], [], []
        self.quiet = quiet
        self.running = False

        kw.pop('start_loop', '')
        kw.pop('port', '')

        try:
            for addr, port, args in _listener_pairs(ports, default_addr=host):
              bind_args = args
              bind_args.update(kw)

              if (bind_args.get('ssl', False) or
                  bind_args.get('ssl_pem', '') == '*'):
                  bind_args.pop('ssl', None)
                  bind_args['ssl_pem'] = '*'

              server = paste.httpserver.serve(app,
                                              port=port,
                                              host=addr,
                                              use_threadpool=True,
                                              daemon_threads=True,
                                              start_loop=False,
                                              **bind_args)
              self.servers.append(server)
              self.startup.append( (server, addr, port) )
        except:
            try:
                self.server_close()
            except:
                pass
            raise
            
    def serve_forever(self, detach=False):
        if self.running: return

        try:
            self.running = True

            while self.startup:
                server, addr, port = self.startup.pop()

                if not self.quiet:
                    sys.stderr.write("Listening on %s:%s\n" % (addr, port))

                if not detach and not self.startup:
                    # Start the final server from calling thread if we're
                    # not detaching.
                    try:
                        server.serve_forever()
                    except KeyboardInterrupt:
                        self.server_close()
                else:
                    thread = Thread(target=server.serve_forever)
                    thread.start()
                    self.threads.append(thread)
        except:
            self.server_close()
            raise

    def server_close(self):
        if not self.quiet:
            sys.stderr.write("Shutting down.\n")
      
        for server in self.servers:      
            try:
                server.server_close()
            except:
                pass

        # FIXME: This feels wrong.  Heck, it all feels wrong.
        while True:
            active = [t for t in self.threads if t.isAlive()]
            if not active:
                break
            active[0].join()

        self.running = False

def _listener_pairs(specs, default_addr='127.0.0.1'):
    """
  Convert flexible port/host:port bind requests into a well-formed
  list of (addr, port, server-arguments) tuples.

  Bind requests can take many forms.  Supply one of the below or a sequence.
    port
    'port'
    'host:port'
    ('host', 'port')
    ('host', port)
    ('host', port, { 'args': 'for httpserver' })

  'default_addr' will be used for host if a host is not provided.  The default
  is a localhost bind.  Specify an IP address or resolvable host or DNS name
  to bind on an alternate IP address, or to bind on all interfaces supply
  None, empty string or '*'.
    """
    if not isinstance(specs, (list, tuple)):
        return _listener_pairs( (specs,), default_addr=default_addr )
  
    bind = []

    for spec in specs:
        if isinstance(spec, int):
            bind.append(_bind(default_addr, spec))
        elif type(spec) is tuple:
            if len(spec) == 2 or len(spec) == 3:
                bind.append(_bind(*spec))
            else:
                raise ValueError()
        elif isinstance(spec, (str,unicode)):
            if spec.index(':') != -1:
                bind.append(_bind( *spec.split(':', 1)))
            else:
                bind.append(_bind(default_addr, spec))
        else:
            raise ValueError("Bogus bind port '%s'." % spec)

    return bind

def _bind (addr, port, args={}):
    return (_canonicalize_bind_addr(addr), int(port), args)


def _canonicalize_bind_addr(addr):
    # Paste 1.0 converts '' to a localhost bind, not 'all-interfaces' like
    # other TCPServer-derived servers.  We also change behavior here, changing
    # "None" to the more natural 'No specific interface to bind'.
    #
    # possible upstream fix:  paste.httpserver.py:558
    #     host = host or '127.0.0.1'
    # to
    #     host = host is None and '127.0.0.1' or host
    if addr is None or addr == '' or addr == '*':
        return '0.0.0.0'
    else:
        return addr

if __name__ == '__main__':
    import time, paste.wsgilib, paste.translogger

    app = paste.translogger.TransLogger(paste.wsgilib.dump_environ)

    serve(app, (8001,
                ':8002',
                ('localhost', 8003, {'ssl': True}),
                ('localhost', 8004, {'ssl_pem': '*'})
                ))
