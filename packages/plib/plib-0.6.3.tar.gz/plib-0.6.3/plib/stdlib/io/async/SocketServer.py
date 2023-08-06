#!/usr/bin/env python
"""
Module SocketServer
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SocketServer class.
"""

from plib.stdlib.io.socket import BaseServer
from plib.stdlib.io.async import SocketDispatcher

class SocketServer(BaseServer, SocketDispatcher):
    """
    Base class for async socket server; dispatches an instance
    of its handler class to handle each request. Pretty much
    a functional equivalent to the Python standard library
    ``SocketServer``, but using async I/O.
    """
    
    def __init__(self, server_addr, handler_class):
        SocketDispatcher.__init__(self)
        BaseServer.__init__(self, server_addr, handler_class)
    
    def close(self):
        SocketDispatcher.close(self)
        self.server_close()
    
    def handle_close(self):
        pass # don't need any warning here
    
    def handle_accept(self):
        conn, addr = self.accept()
        self.handler(conn, addr, self)
    
    def serve_forever(self, callback=None):
        self.do_loop(callback) # simple alias for API compatibility
