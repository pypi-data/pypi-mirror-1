#!/usr/bin/env python
"""
Module PTCPClient
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PTCPClient class.
"""

import sys
import socket

class PTCPClient(object):
    """
    Client class that connects with TCP server and maps socket
    methods to client methods, so it can be used with SendReceiveMixin
    to simplify data reads and writes.
    """
    
    server_name = "server"
    server_addr = ("localhost", 9999)
    
    def __init__(self):
        # Set up socket
        self._sock = socket.socket() # defaults to AF_INET, SOCK_STREAM
        self.sendall = self._sock.sendall
        self.recv = self._sock.recv
        
        # Connect to server
        self.sock_result = self._sock.connect_ex(self.server_addr)
        if self.sock_result != 0:
            sys.stderr.write("%s connection failed.\n" % self.server_name)
    
    def __del__(self):
        self._sock.close()
