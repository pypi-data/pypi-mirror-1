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

import socket
from errno import EINTR
try:
    from errno import ERESTART # won't work on OS X
except ImportError:
    ERESTART = None # safe alternate

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
        and do controlled shutdown on a terminating signal.
        """
        
        try:
            while self.terminate_sig is None:
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
