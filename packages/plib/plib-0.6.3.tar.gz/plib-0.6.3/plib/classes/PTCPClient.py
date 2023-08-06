#!/usr/bin/env python
"""
Module PTCPClient
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PTCPClient class. This is a
blocking socket I/O client that connects to a server,
writes a given data string, and stores the server's
reply in self.read_data. The process_data method should
be overridden to do something with the returned data;
note that this method will be called from *inside* the
client_communicate method, and when it is finished, the
read data will be cleared.
"""

import sys
import socket

from plib.stdlib.SocketClient import SocketClient

class PTCPClient(SocketClient):
    """
    Client class that connects with TCP server, writes data,
    and stores the reply.
    """
    
    raise_error = True
    server_name = "server"
    server_addr = ("localhost", 9999)
    
    def client_communicate(self, data):
        """
        Method overridden to add error handling and reporting.
        """
        
        try:
            try:
                SocketClient.client_communicate(self, data, self.server_addr)
            except socket.error:
                sys.stderr.write("failed to connect to %s at %s, port %s.\n" %
                    (self.server_name,) + self.server_addr)
                if self.raise_error:
                    raise
        finally:
            self.close()
