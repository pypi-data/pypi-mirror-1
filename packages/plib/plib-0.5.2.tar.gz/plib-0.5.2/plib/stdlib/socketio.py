#!/usr/bin/env python
"""
Module SOCKETIO -- Base I/O Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements socket-specific I/O functionality
that is useful in both blocking and non-blocking modes.
"""

import os
import socket
from errno import ENOTCONN, EISCONN, EBADF, errorcode

from plib.stdlib.io import BaseData

class SocketIOBase(object):
    """
    Base class for socket I/O functionality. Overlays the
    underlying socket object methods with error checking
    and handling.
    """
    
    accepting = False
    addr = None
    closed = False
    connected = False
    
    def __init__(self, sock=None):
        if sock:
            try:
                self.addr = sock.getpeername()
                self.connected = True # will only get here if connected
            except socket.error, err:
                if err[0] == ENOTCONN:
                    # To handle the case where we got an unconnected
                    # socket; self.connected is False by default
                    pass
                else:
                    raise
            self.set_socket(sock)
        else:
            self.socket = None
    
    def create_socket(self, family, type):
        self.set_socket(socket.socket(family, type))
    
    def set_socket(self, sock):
        self.socket = sock
    
    def set_reuse_addr(self):
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) | 1)
        except socket.error:
            pass
    
    def listen(self, num):
        self.accepting = True
        if os.name == 'nt' and num > 5:
            num = 1
        return self.socket.listen(num)
    
    def bind(self, addr):
        self.addr = addr
        return self.socket.bind(addr)
    
    def accept(self):
        return self.socket.accept()
    
    def connect(self, address):
        self.connected = False
        err = self.socket.connect_ex(address)
        # FIXME: Add Winsock return values?
        if err in (0, EISCONN):
            self.addr = address
            self.connected = True
            self.closed = False
        else:
            raise socket.error, (err, errorcode[err])
    
    def send(self, data):
        try:
            return self.socket.send(data)
        except socket.error:
            self.close()
            raise
    
    def recv(self, buffer_size):
        try:
            data = self.socket.recv(buffer_size)
            if not data:
                # if recv returns 0 bytes, connection is closed
                self.close()
                return ''
            return data
        except socket.error:
            self.close()
            raise
    
    def close(self):
        if not self.closed:
            self.accepting = False
            self.connected = False
            try:
                self.socket.close()
                self.closed = True
            except socket.error, why:
                if why[0] in (ENOTCONN, EBADF):
                    self.closed = True
                else:
                    raise

class SocketData(BaseData):
    """
    Basic data handling for socket I/O; intended to
    mixin with a derived class of SocketIOBase.
    """
    
    bufsize = 4096
    
    def dataread(self, bufsize):
        return self.recv(self.bufsize)
    
    def datawrite(self, data):
        return self.send(self.write_data)

class ConnectMixin(object):
    """
    Mixin class to add socket connect functionality. Usable by both
    "one-loop" and persistent clients.
    """
    
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    
    def do_connect(self, addr):
        """ Convenience method to create socket and connect to addr. """
        self.create_socket(self.address_family, self.socket_type)
        self.connect(addr)

class SocketClientMixin(ConnectMixin):
    """
    Mixin class for socket clients, implements setup_client method
    (which is called from client_communicate).
    """
    
    def setup_client(self, addr=None):
        if addr is not None:
            self.do_connect(addr)

class SocketServerMixin(object):
    
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
