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
from errno import EWOULDBLOCK, ECONNRESET, ENOTCONN, ESHUTDOWN, \
    ECONNABORTED, EISCONN, EBADF, errorcode

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
        try:
            conn, addr = self.socket.accept()
            return conn, addr
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return (None, None)
            else:
                raise
    
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
            result = self.socket.send(data)
            return result
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return 0
            elif why[0] in (ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED):
                self.close()
                return 0
            else:
                raise
    
    def recv(self, buffer_size):
        try:
            data = self.socket.recv(buffer_size)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.close()
                return ''
            else:
                return data
        except socket.error, why:
            # winsock sometimes throws ENOTCONN
            if why[0] in [ECONNRESET, ENOTCONN, ESHUTDOWN]:
                self.close()
                return ''
            else:
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

class SocketIO(SocketIOBase, BaseData):
    """
    Socket I/O class that adds basic data handling.
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
