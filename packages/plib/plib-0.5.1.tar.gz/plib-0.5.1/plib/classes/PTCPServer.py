#!/usr/bin/env python
"""
Module PTCPServer
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PTCPServer class. This is a forking
TCP server that includes the general signal handling and
logging facilities of PServerBase.
"""

from plib.stdlib.SigSocketServer import BaseRequestHandler, SigForkingTCPServer

from PServerBase import PServerBase

class PTCPServer(PServerBase, SigForkingTCPServer):
    """
    Generic forking TCP server class. Adds handling of the
    terminate_sig flag to serve_forever.
    """
    
    bind_addr = ("localhost", 9999)
    handler_class = BaseRequestHandler
    
    def __init__(self):
        PServerBase.__init__(self)
        SigForkingTCPServer.__init__(self, self.bind_addr, self.handler_class)
    
    def server_close(self):
        SigForkingTCPServer.server_close(self)
        PServerBase.server_close(self)
    
    def serve_forever(self):
        """
        Modify method to check termination flag at every loop iteration
        # and to do controlled shutdown on a terminating signal.
        """
        
        try:
            while self.terminate_sig is None:
                self.handle_request()
        finally:
            self.server_close()
