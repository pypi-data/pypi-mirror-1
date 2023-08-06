#!/usr/bin/env python
"""
Module SOCKET -- Socket I/O Handling
Sub-Package STDLIB.IO.SOCKET of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements socket-specific I/O functionality
that is useful in both blocking and non-blocking modes.
"""

import os
import socket
from errno import EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, \
    EISCONN, EBADF, errorcode

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
        except socket.error, why:
            self.close()
            if why[0] in (EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED):
                return 0
            else:
                raise
    
    def recv(self, buffer_size):
        try:
            # NOTE: A recv of zero bytes means the socket on the other end has
            # closed, so you might think we'd check for that here and call
            # ``self.close()`` if it happens; however, doing that would break
            # a read/write strategy that let the other end call ``shutdown``
            # when it was finished sending but could still receive (e.g., see
            # the ``ShutdownReadWrite`` class). So we need to leave it to
            # higher-level code (mainly the read/write handling classes) to
            # decide how to handle zero-byte reads.
            return self.socket.recv(buffer_size)
        except socket.error, why:
            self.close()
            if why[0] in (EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED):
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
                if why[0] in (ENOTCONN, EBADF, EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED):
                    self.closed = True
                else:
                    raise

class SocketData(BaseData):
    """
    Basic data handling for socket I/O; intended to
    mixin with a derived class of ``SocketIOBase``.
    """
    
    bufsize = 4096
    
    def dataread(self, bufsize):
        return self.recv(self.bufsize)
    
    def datawrite(self, data):
        return self.send(self.write_data)
