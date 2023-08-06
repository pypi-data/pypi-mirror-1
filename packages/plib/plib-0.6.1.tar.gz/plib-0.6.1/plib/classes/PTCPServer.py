#!/usr/bin/env python
"""
Module PTCPServer
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PTCPServer`` class. This is a forking
TCP server that includes the general signal handling and
logging facilities of ``PServerBase``.
"""

from plib.stdlib.io.blocking import BaseRequestHandler, SocketServer

from PServerBase import PServerBase

class PTCPServer(PServerBase, SocketServer):
    """
    Generic forking TCP server class. Adds handling of the
    ``terminate_sig`` flag to the ``keep_running`` check.
    """
    
    bind_addr = ("localhost", 9999)
    handler_class = BaseRequestHandler
    
    def __init__(self):
        PServerBase.__init__(self)
        SocketServer.__init__(self, self.bind_addr, self.handler_class)
    
    def server_close(self):
        SocketServer.server_close(self)
        PServerBase.server_close(self)
    
    def keep_running(self):
        return SocketServer.keep_running(self) and (self.terminate_sig is None)
