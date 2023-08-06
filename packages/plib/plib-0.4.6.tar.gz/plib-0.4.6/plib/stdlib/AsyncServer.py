#!/usr/bin/env python
"""
Module ASYNCSERVER -- Asynchronous Socket Client/Server Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module defines asynchronous I/O classes based on
the dispatcher class in the async module of this sub-package,
specialized for use with network sockets to give functionality
basically the same as asyncore.dispatcher (in the BaseDispatcher
class), and then, built on this, asynchronous server/request
handler classes with similar functionality to the BaseServer
and BaseRequestHandler classes in the SocketServer module,
and a client class that can communicate with them.

Note that the client and server communicator functions are
provided in mixin classes, so that alternative read and
write handling can be substituted for the defaults in
the base classes here. The actual "communicator" classes in this
module should only be used if the default read/write handling
is all that is needed; otherwise the mixins should be used.
See the docstring of the ReadWrite module for more details.
"""

import os
import socket
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EISCONN, errorcode

from plib.stdlib.async import AsyncBase, BaseData, ClientMixin, ServerMixin

class BaseDispatcher(AsyncBase):
    """
    Dispatcher class that fixes a number of minor issues
    with asyncore.dispatcher. Key changes:
    
    -- handle_error is changed to close the socket and then
       re-raise whatever exception caused it to be called
       (much more Pythonic)
    
    -- handle_close is called from close, instead of the
       reverse (having the method that's intended to be
       a placeholder call a method that needs to always be
       called makes no sense)
    
    -- correctly handles the case where a non-blocking
       connect attempt fails: asyncore.dispatcher ends up
       bailing to handle_error on the first read or write
       attempt to the socket, but aside from being ugly,
       this doesn't work if the dispatcher won't return
       True for readable or writable until it knows the
       connect has succeeded--it will just hang forever in
       the polling loop--but this class spots the socket
       error and raises an exception so the loop exits
    
    This class also allows a callback function on
    each iteration of the polling loop. This allows other
    processing to be done while waiting for network I/O
    (one common use case would be keeping a GUI event loop
    running concurrently with the network polling loop).
    """
    
    accepting = False
    addr = None
    connected = False
    connect_pending = False
    
    def __init__(self, sock=None, map=None):
        AsyncBase.__init__(self, map)
        
        if sock:
            self.set_socket(sock, map)
            try:
                self.addr = sock.getpeername()
            except socket.error:
                pass
        else:
            self.socket = None
    
    def repr_status(self, status):
        if self.accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
    
    def create_socket(self, family, type):
        self.set_socket(socket.socket(family, type))
    
    def set_socket(self, sock, map=None):
        self.socket = sock
        self.socket.setblocking(0)
        self.set_fileobj(sock, map)
    
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
    
    def connect(self, address):
        self.connected = False
        self.connect_pending = False
        err = self.socket.connect_ex(address)
        # FIXME: Add Winsock return values?
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            # The connect will be completed asynchronously, so
            # set a flag to signal that we're waiting
            self.connect_pending = True
            return
        if err in (0, EISCONN):
            self.addr = address
            self.connected = True
            self.handle_connect()
        else:
            raise socket.error, (err, errorcode[err])
    
    def accept(self):
        try:
            conn, addr = self.socket.accept()
            return conn, addr
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return (None, None)
            else:
                raise
    
    def send(self, data):
        try:
            result = self.socket.send(data)
            return result
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
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
        # This is the method that should be called from all the
        # places that call handle_close in asyncore.dispatcher
        AsyncBase.close(self)
        self.socket.close()
        self.connected = False
        self.connect_pending = False
        self.handle_close()
    
    def check_connect(self):
        if self.connect_pending:
            # We're waiting for a connect to be completed
            # asynchronously, so we need to see if it really
            # was completed or if an error occurred
            err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err:
                # Re-raise the error so the connect aborts
                raise socket.error, (err, errorcode[err])
            
            # If we get here, the connect was successful, so
            # fill in the address
            self.addr = self.socket.getpeername()
            self.connect_pending = False
        
        # Always set this flag since we only get called if
        # it wasn't already set--if connect_pending was false,
        # then our socket was assigned in the constructor
        # (probably because we're a server-side request handler)
        # and we can just assume we're connected
        self.connected = True
    
    def handle_read_event(self):
        if self.accepting:
            # Handle the accept--this should be the only read
            # we ever see, since we hand off the actual connection
            # to another socket
            self.handle_accept()
        else:
            # Getting a read implies that we are connected, so
            # we first check to see if we were waiting for a connect
            # to be completed asynchronously and verify it if so
            if not self.connected:
                self.check_connect()
                self.handle_connect()
            self.handle_read()
    
    def handle_write_event(self):
        # Getting a write implies that we are connected, so
        # same logic as for handle_read_event above
        if not self.connected:
            self.check_connect()
            self.handle_connect()
        self.handle_write()
    
    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    def __getattr__(self, attr):
        return getattr(self.socket, attr)
    
    def handle_expt(self):
        # This corrects the log_info description (asyncore.dispatcher
        # says 'exception' which isn't correct)
        self.log_info('unhandled out of band data', 'warning')
    
    def handle_connect(self):
        self.log_info('unhandled connect event', 'warning')
    
    def handle_accept(self):
        self.log_info('unhandled accept event', 'warning')
    
    def handle_close(self):
        # This gets called _from_ close(), not the other way around,
        # so eliminate the close() call here
        self.log_info('unhandled close event', 'warning')

class BaseSocket(BaseData, BaseDispatcher):
    """
    Socket dispatcher class that adds basic read/write handling.
    Note that the read/write handling can be modified by mixing
    in other handlers (e.g., those in the ReadWrite module).
    """
    
    bufsize = 4096
    read_done = False
    
    def clear_data(self):
        super(BaseSocket, self).clear_data()
        self.read_done = False
    
    def handle_read(self):
        """
        Reads one buffer's worth of data; sets read_done flag if
        no data was returned.
        """
        
        received = self.recv(self.bufsize)
        if received:
            self.read_data += received
        else:
            self.read_done = True
    
    def read_complete(self):
        return self.read_done
    
    def handle_write(self):
        """
        Writes one buffer's worth of data and removes
        written data from write buffer.
        """
        
        sent = self.send(self.write_data)
        self.write_data = self.write_data[sent:]
    
    def write_complete(self):
        return not self.write_data
    
    def handle_close(self):
        pass # don't need any warning here

class ClientSocketMixin(ClientMixin):
    """
    Mixin class for socket client. The writable and readable
    methods need to return True if a connect is pending (to make
    sure we get notified when the asynchronous connect completes;
    it could be either a read or a write select() return so we
    allow for both to be safe). Derived classes should override
    handle_connect to do initial setup of self.write_data (best
    done there so no processing is wasted on a failed connect).
    """
    
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    
    def writable(self):
        return self.connect_pending or ClientMixin.writable(self)
    
    def readable(self):
        return self.connect_pending or ClientMixin.readable(self)
    
    def do_connect(self, addr):
        """
        Convenience method to create socket and connect to addr.
        """
        
        self.create_socket(self.address_family, self.socket_type)
        self.connect(addr)
    
    def client_communicate(self, addr, callback=None):
        """
        Convenience method to implement the "standard" client
        pattern: connect to addr, write data, read data back.
        Assumes that this client is the "master" async object
        in the program, so that its do_loop runs the async
        polling loop (if this is *not* the "master" async object,
        use do_connect instead).
        """
        
        self.do_connect(addr)
        self.do_loop(callback)

class ClientCommunicator(ClientSocketMixin, BaseSocket): pass

class ServerSocketMixin(ServerMixin):
    """
    Mixin for server-side socket; just adds a default handle_connect
    method to overlay on BaseDispatcher and suppress the warning.
    """
    
    def handle_connect(self):
        pass # don't need any warning here

class ServerCommunicator(ServerSocketMixin, BaseSocket): pass

class BaseRequestHandler(BaseSocket):
    """
    Dispatcher class set up to serve as a request handler.
    """
    
    def __init__(self, request, client_address, server):
        BaseDispatcher.__init__(self, request)
        self.client_address = client_address
        self.server = server

class AsyncRequestHandler(ServerSocketMixin, BaseRequestHandler): pass

class ServerDispatcher(BaseDispatcher):
    """
    Class for the actual server; dispatches an instance of
    its communicator class to handle each request. Pretty much
    a functional equivalent to SocketServer but using asyncore
    to allow multiplexing in a single process.
    """
    
    address_family = socket.AF_INET
    allow_reuse_address = False
    request_queue_size = 5
    socket_type = socket.SOCK_STREAM
    
    def __init__(self, server_addr, handler_class):
        BaseDispatcher.__init__(self)
        self.handler = handler_class
        
        self.create_socket(self.address_family, self.socket_type)
        if self.allow_reuse_address:
            self.set_reuse_addr()
        self.bind(server_addr)
        self.listen(self.request_queue_size)
    
    def server_close(self):
        self.close()
    
    def handle_close(self):
        pass # don't need any warning here
    
    def handle_accept(self):
        conn, addr = self.accept()
        self.handler(conn, addr, self)
    
    def serve_forever(self, callback=None):
        try:
            self.do_loop(callback)
        finally:
            self.server_close()
