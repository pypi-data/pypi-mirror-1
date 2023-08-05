#!/usr/bin/env python
"""
Module PRequestHandler
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PRequestHandler class.
"""

import SocketServer

class PRequestHandler(SocketServer.BaseRequestHandler):
    """
    Request Handler class for generic server; maps socket send and
    receive methods to handler methods so it can be used with the
    SendReceiveMixin class to simplify data reads and writes.
    """
    
    def __init__(self, request, client_address, server):
        # Map request send/recv methods to ours
        self.sendall = request.sendall
        self.recv = request.recv
        
        # This will now do all the work
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
