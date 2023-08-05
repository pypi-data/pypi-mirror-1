#!/usr/bin/env python
"""
Module SigSocketServer
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

This module contains extensions to the SocketServer module
in the Python standard library.
"""

import signal
import SocketServer

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
