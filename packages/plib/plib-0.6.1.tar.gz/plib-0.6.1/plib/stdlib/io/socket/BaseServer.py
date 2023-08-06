#!/usr/bin/env python
"""
Module BaseServer
Sub-Package STDLIB.IO.SOCKET of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the socket BaseServer class.
"""

import socket

class BaseServer(object):
    """
    Base socket server class; sets up socket to listen on
    specified address.
    """
    
    address_family = socket.AF_INET
    allow_reuse_address = False
    request_queue_size = 5
    socket_type = socket.SOCK_STREAM
    
    def __init__(self, server_addr, handler_class):
        self.handler = handler_class
        
        self.create_socket(self.address_family, self.socket_type)
        if self.allow_reuse_address:
            self.set_reuse_addr()
        self.bind(server_addr)
        self.listen(self.request_queue_size)
    
    def handle_error(self):
        """ Print the error info and continue (should *not* shut down the server!) """
        
        print "-"*40
        print "Exception thrown!"
        import traceback
        traceback.print_exc() # XXX But this goes to stderr!
        print "-"*40
    
    def server_close(self):
        """ Placeholder for derived classes. """
        
        pass
