#!/usr/bin/env python
"""
Module SocketServer
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a simplified alternate to the SocketServer
class from the Python standard library. The key changes are:

- Simpler method structure (based on the general I/O methods
  used by all modules in this sub-package)
- The only server class is the forking TCP server; for the
  use cases in view, it is assumed that handling more than one
  request at a time is desired (so simple synchronous TCP is
  out), and if shared state between the server and request
  handlers is desired, it's much easier to use the async I/O
  modules in this sub-package instead of trying to deal with
  threads, so no threading support is given. (Also, since the
  UDP implementation wouldn't work on Linux anyway, I didn't
  see any point in including it.)
- The forking server responds to SIGCHLD by trying to reap
  finished children.
- No attempt is made to implement a timeout while listening
  for requests (as is done in Python 2.6 and later) or to
  allow shutdown of the server via a method call from another
  thread (as is done in Python 2.6 and later--since we don't
  offer a threaded implementation, there's no point). As far
  as I can tell, the reason for adding the timeout functionality
  in Python 2.6 was to support PyGTK, but I have a hard time
  seeing why you'd want to run a server in the same process as
  a GUI event loop. Servers are *supposed* to be run in their
  own processes; a GUI to make use of the server's functionality
  should be a *client*, talking to the server through a socket.
  (And if you want to do that with a client, the client should
  be using asynchronous I/O anyway--see the client classes in
  the plib.stdlib.io.async sub-package.)
"""

import os
import socket
from errno import EINTR
try:
    from errno import ERESTART # won't work on OS X
except ImportError:
    ERESTART = None # safe alternate

from plib.stdlib.io.socket import BaseServer, SocketIOBase
from plib.stdlib.io.blocking import SigMixin

class _BaseTCPServer(BaseServer, SocketIOBase):
    """
    Base forking TCP server; forks a new process for each
    request and instantiates a request handler in the child.
    This implementation is factored out from ``SigMixin``
    so that the SIGCHLD-handling functionality can be grafted
    onto other server classes if desired (see the ``SigMixin``
    docstring).
    """
    
    active_children = None
    
    def __init__(self, server_addr, handler_class):
        SocketIOBase.__init__(self)
        BaseServer.__init__(self, server_addr, handler_class)
    
    def collect_children(self):
        """Internal routine to wait for children that have exited."""
        
        if self.active_children is None:
            return
        
        # XXX: This loop runs more system calls than it ought
        # to. There should be a way to put the active_children into a
        # process group and then use os.waitpid(-pgid) to wait for any
        # of that set, but I couldn't find a way to allocate pgids
        # that couldn't collide.
        for child in self.active_children:
            try:
                pid, status = os.waitpid(child, os.WNOHANG)
            except os.error:
                pid = None
            if not pid:
                continue
            try:
                self.active_children.remove(pid)
            except ValueError:
                pass # no point in raising an exception here, just go on
    
    def fork_request(self, request, client_address):
        """Fork a new subprocess to process the request."""
        
        self.collect_children()
        pid = os.fork()
        if pid:
            # Parent process
            if self.active_children is None:
                self.active_children = []
            self.active_children.append(pid)
            request.close()
            return
        else:
            # Child process.
            # This must never return, hence os._exit()!
            try:
                self.handler(request, client_address, self)
                os._exit(0)
            except:
                try:
                    self.handle_error()
                    request.close()
                finally:
                    os._exit(1)
        raise RuntimeError, "fork_request exit should be unreachable!"
    
    def handle_request(self):
        """ Get the request info and fork a handler. """
        
        conn, addr = self.accept()
        self.fork_request(conn, addr)
    
    def keep_running(self):
        """ Check whether the server should break out of the serve_forever loop. """
        
        return True
    
    def serve_forever(self):
        """
        Handle requests until doomsday. Ensure server socket is
        closed on an exception.
        """
        
        try:
            while self.keep_running():
                # If we get an 'interrupted system call', don't shut
                # down, just re-start the accept()
                try:
                    self.handle_request()
                except socket.error, why:
                    if why[0] in (EINTR, ERESTART):
                        continue
                    else:
                        raise
        finally:
            self.server_close()

class SocketServer(SigMixin, _BaseTCPServer):
    """
    Forking TCP server with child signal handling. Note that we use the
    collect_on_signal flag to delay reaping children until the while loop
    calls keep_running; this avoids some potential issues with reaping
    children while we're inside the accept() system call.
    """
    
    collect_on_signal = False # we do it in keep_running instead
    
    def __init__(self, server_addr, handler_class):
        SigMixin.__init__(self)
        _BaseTCPServer.__init__(self, server_addr, handler_class)
    
    def keep_running(self):
        """
        If we received SIGCHLD, it will break us out of ``handle_request``,
        so we can just reap children here before we re-start the system call.
        """
        
        if self.child_waiting:
            self.collect_children()
        return True
