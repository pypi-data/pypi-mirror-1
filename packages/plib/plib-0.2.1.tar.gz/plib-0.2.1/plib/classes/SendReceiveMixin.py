#!/usr/bin/env python
"""
Module SendReceiveMixin
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the SendReceiveMixin class.
"""

class SendReceiveMixin(object):
    """
    Mixin class to define basic send/receive logic for sockets. 
    Can be used on both the client and server sides, but expects to
    be mixed in with a class that defines the standard socket sendall
    and recv methods.
    """
    
    bufsize = 4096
    
    def send_data(self, data):
        """ Send data string through socket connection. """
        
        self.sendall(data)
    
    def recv_data(self):
        """ Receive data through socket connection and return as string. """
        
        # TODO: There's gotta be a better way to do this
        rlist = []
        while 1:
            data = self.recv(self.bufsize)
            if len(data) < 1:
                break
            rlist.append(data)
            # TODO: Why do we need this check in addition to above?
            if len(data) < self.bufsize:
                break
        return "".join(rlist)
