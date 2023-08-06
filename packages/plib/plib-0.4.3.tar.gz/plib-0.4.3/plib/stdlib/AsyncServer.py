#!/usr/bin/env python
"""
Module ASYNCSERVER -- Asynchronous Client/Server Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module defines client and server classes based on
the dispatcher class in the async module of this sub-package.
These classes provide base implementations of an asynchronous
server/request handler with similar functionality to the
BaseServer and BaseRequestHandler classes in the SocketServer
module, and a client class that can communicate with them.
All of these objects can communicate while still allowing
other program functions to run when they are waiting on network
I/O (for example, a GUI event handler loop can be kept "alive"
along with the network connection).

Note that the client and server communicator functions are
provided in mixin classes, so that alternative read and
write handling can be substituted for the defaults in
BaseCommunicator. The actual "communicator" classes in this
module should only be used if the default read/write handling
is all that is needed; otherwise the mixins should be used.
An example of using the mixins with an alternate read/write
mixin is given in the plib.classes.ReadWrite docstring.
"""

import socket

from async import BaseDispatcher

class BaseCommunicator(BaseDispatcher):
    """
    Basic async communicator class using ReadWrite.
    """
    
    def __init__(self, sock=None):
        self.clear_data()
        self.done = False
        BaseDispatcher.__init__(self, sock)
    
    def clear_data(self):
        self.write_data = ""
        self.read_data = ""
        self.read_done = False
    
    def handle_read(self):
        """
        Reads one buffer's worth of data; sets flag if
        no data was returned.
        """
        
        received = self.recv(self.bufsize)
        if received:
            self.read_data += received
        else:
            self.read_done = True
    
    def handle_write(self):
        """
        Writes one buffer's worth of data and removes
        written data from write buffer.
        """
        
        sent = self.send(self.write_data)
        self.write_data = self.write_data[sent:]
    
    def read_complete(self):
        return self.read_done
    
    def write_complete(self):
        return not self.write_data
    
    def query_done(self):
        """
        Should return True if no further read/write operations
        are necessary. Default is to always return True, which
        means that as soon as self.write_data and self.read_data
        have both been processed once, we are done and the object
        will close.
        """
        return True
    
    def check_done(self):
        """
        This method is intended to be called whenever a single "pass"
        of the read/write cycle completes (i.e., self.write_data
        and self.read_data have each been processed once).
        """
        
        if self.query_done():
            self.done = True
            self.close()
    
    def handle_close(self):
        self.clear_data()

class ClientMixin(object):
    """
    Mixin class for client programs; writes data first, then
    reads back the response. Note that the writable and readable
    methods need to return True if a connect is pending (to make
    sure we get notified when the asynchronous connect completes;
    it could be either a read or a write select() return so we
    allow for both to be safe).
    """
    
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    
    def writable(self):
        return self.connect_pending or not self.write_complete()
    
    def readable(self):
        return self.connect_pending or not (self.writable() or self.done)
    
    def handle_read(self):
        super(ClientMixin, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.check_done()
    
    def process_data(self):
        """
        Derived classes should override to process self.read_data
        and determine whether check_done should return True. Note
        that the initial setup of self.write_data can be done in
        the constructor or by overriding handle_connect (the
        latter is recommended so you don't waste processing on a
        failed connect).
        """
        pass
    
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

class ClientCommunicator(ClientMixin, BaseCommunicator): pass

class ServerMixin(object):
    """
    Mixin for server-side programs; reads data first, then
    writes back the response after processing. This base class
    provides simple "echo" functionality--the input is just
    copied to the output with no other processing. Subclasses
    should override process_data to do something more.
    """
    
    def handle_connect(self):
        pass # don't need any warning here
    
    def readable(self):
        return not self.read_complete()
    
    def handle_read(self):
        super(ServerMixin, self).handle_read()
        if self.read_complete():
            self.process_data()
    
    def writable(self):
        return not (self.readable() or self.write_complete() or self.done)
    
    def handle_write(self):
        super(ServerMixin, self).handle_write()
        if self.write_complete():
            self.check_done()
    
    def process_data(self):
        """
        Derived classes should override to do something more than
        just echo input to output.
        """
        self.write_data = self.read_data

class ServerCommunicator(ServerMixin, BaseCommunicator): pass

class BaseRequestHandler(BaseCommunicator):
    """
    Communicator class set up to serve as a request handler.
    """
    
    def __init__(self, request, client_address, server):
        BaseCommunicator.__init__(self, request)
        self.client_address = client_address
        self.server = server

class AsyncRequestHandler(ServerMixin, BaseRequestHandler): pass

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
