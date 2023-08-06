#!/usr/bin/env python
"""
Module SigSocketServer
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains extensions to the SocketServer module
in the Python standard library.
"""

import sys
import signal
import SocketServer

from plib.stdlib.socketio import SocketIO
from plib.stdlib.ClientServer import RequestMixin

class BaseRequestHandler(RequestMixin, SocketIO):
    """
    Basic blocking I/O request handler; default is to do one
    round-trip exchange of data and then shut down.
    """
    
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        SocketIO.__init__(self, request)
        try:
            self.server_communicate()
        finally:
            # We don't have to close ourselves here, the server will do it
            sys.exc_traceback = None # Help garbage collection

class SigMixin(object):
    """
    Mixin class for forking servers to collect children when they
    exit instead of waiting for the next request. Note that since this
    class overrides collect_children, it must be before the forking
    server class in the list of bases.
    """
    
    def __init__(self):
        """
        Call this before calling the server __init__.
        """
        
        signal.signal(signal.SIGCHLD, self.child_sig_handler)
        self.collecting = False
    
    def child_sig_handler(self, sig, frame):
        """
        Respond to SIGCHLD by collecting dead children.
        """
        
        self.collect_children()
    
    def collect_children(self):
        """
        Wrap method to prevent re-entrant calls (the superclass
        collect_children will loop until all dead children are
        collected anyway, so ignoring overlapping calls is OK).
        """
        
        if not self.collecting:
            self.collecting = True
            super(SigMixin, self).collect_children()
            self.collecting = False
    
    def serve_forever(self):
        """
        Modify method to ensure server socket is closed on an
        exception.
        """
        
        try:
            while 1:
                self.handle_request()
        finally:
            self.server_close()

class SigForkingTCPServer(SigMixin, SocketServer.ForkingTCPServer):
    """
    Forking TCP server with child signal handling.
    """
    
    def __init__(self, server_address, RequestHandlerClass):
        SigMixin.__init__(self)
        SocketServer.ForkingTCPServer.__init__(self, server_address, RequestHandlerClass)

class SigForkingUDPServer(SigMixin, SocketServer.ForkingUDPServer):
    """
    Forking UDP server with child signal handling.
    """
    
    def __init__(self, server_address, RequestHandlerClass):
        SigMixin.__init__(self)
        SocketServer.ForkingUDPServer.__init__(self, server_address, RequestHandlerClass)
