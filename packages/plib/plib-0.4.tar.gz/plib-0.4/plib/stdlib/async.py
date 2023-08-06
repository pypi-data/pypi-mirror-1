#!/usr/bin/env python
"""
Module ASYNC -- Asynchronous Client/Server Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains classes that build on the asyncore
module in the Python standard library. These classes provide
base implementations of an asynchronous server/request
handler with similar functionality to the BaseServer and
BaseRequestHandler classes in the SocketServer module, and
an asynchronous client that can communicate with a server
while still allowing other program functions to run while
waiting on network I/O (for example, a GUI event handler loop
can be kept "alive" along with the network client).
"""

import asyncore
import socket

class BaseDispatcher(asyncore.dispatcher):
    """
    Dispatcher class that allows a callback function on
    each iteration of the polling loop. This allows other
    processing to be done while waiting for network I/O
    (one common use case would be keeping a GUI event loop
    running concurrently with the network polling loop).
    """
    
    poll_timeout = 1.0
    
    def do_loop(self, callback=None):
        if callback:
            map = self._map #asyncore.socket_map
            fn = asyncore.poll
            t = self.poll_timeout
            while map:
                callback()
                fn(t, map)
        else:
            # Don't need shorter timeout here since there's no callback
            asyncore.loop()

class ReadWrite:
    """
    Basic read/write class that converts back and forth
    between simple string data and formatted data that
    has the content length in front. When writing, it
    takes self.write_data and formats it as below; when
    reading, it assumes the incoming data is formatted
    as below and extracts the content into self.read_data.
    (Note that the read_data and write_data fields may be
    clobbered at any time, so data that needs to be static
    should be duplicate stored in another variable.)
    
    Data format: <content-length>\r\n<content>
    """
    
    bufsize = 4096
    
    def __init__(self):
        self.write_data = ""
        self.formatted = False
        self.read_data = ""
        self.read_len = -1
        self.bytes_read = 0
        self.done = False
    
    def format_buffer(self, data):
        """ Encodes data length at front of data. """
        
        return "%s\r\n%s" % (str(len(data)), data)
    
    def unformat_buffer(self, data):
        """ Splits encoded data into length and content. """
        
        lstr, received = data.split("\r\n", 1)
        return int(lstr), received
    
    def handle_write(self):
        """
        Formats data first if not yet formatted; writes one
        buffer's worth of data, returns True if all data has
        been written.
        """
        
        if not self.formatted:
            self.write_data = self.format_buffer(self.write_data)
            self.formatted = True
        sent = self.send(self.write_data)
        self.write_data = self.write_data[sent:]
        return not self.write_data
    
    def handle_read(self):
        """
        Unformats incoming data first if content length not yet
        extracted; reads one buffer's worth of data, returns
        True if all data has been read.
        """
        
        received = self.recv(self.bufsize)
        if received:
            if self.read_len < 0:
                self.read_len, received = self.unformat_buffer(received)
            self.bytes_read += len(received)
            self.read_data = self.read_data + received
        return self.bytes_read >= self.read_len

class BaseCommunicator(ReadWrite, BaseDispatcher):
    """
    Basic async communicator class using ReadWrite.
    """
    
    def __init__(self, sock=None):
        ReadWrite.__init__(self)
        BaseDispatcher.__init__(self, sock)
    
    def handle_connect(self):
        pass # need this to make asyncore happy
    
    def handle_close(self):
        self.close() # eliminate asyncore's warning here

class ClientCommunicator(BaseCommunicator):
    """
    Communicator for client programs; writes data first, then
    reads back the response.
    """
    
    address_family = socket.AF_INET
    failed = "Connect failed."
    socket_type = socket.SOCK_STREAM
    
    def do_connect(self, addr):
        self.create_socket(self.address_family, self.socket_type)
        try:
            self.connect(addr)
        except socket.error:
            return self.failed
        return None
    
    def writable(self):
        return (len(self.write_data) > 0)
    
    def readable(self):
        return not (self.writable() or self.done)
    
    def handle_read(self):
        if BaseCommunicator.handle_read(self):
            self.done = True
            self.close()
            return True
        return False

class ServerCommunicator(BaseCommunicator):
    """
    Communicator for server programs; reads data first, then
    writes back the response after processing. This base class
    provides simple "echo" functionality--the input is just
    copied to the output with no other processing. Subclasses
    should override process_data to do something more.
    """
    
    def readable(self):
        return (self.read_len < 0) or (self.bytes_read < self.read_len)
    
    def handle_read(self):
        if BaseCommunicator.handle_read(self):
            self.process_data()
            return True
        return False
    
    def writable(self):
        return (not self.readable()) and (len(self.write_data) > 0) and not self.done
    
    def handle_write(self):
        if BaseCommunicator.handle_write(self):
            self.done = True
            self.close()
            return True
        return False
    
    def process_data(self):
        self.write_data = self.read_data

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
    
    def __init__(self, server_addr=("localhost", 9999), handler_class=ServerCommunicator):
        BaseDispatcher.__init__(self)
        self.handler_class = handler_class
        
        self.create_socket(self.address_family, self.socket_type)
        if self.allow_reuse_address:
            self.set_reuse_addr()
        self.bind(server_addr)
        self.listen(self.request_queue_size)
    
    def handle_accept(self):
        conn, addr = self.accept()
        self.handler_class(conn)
    
    def serve_forever(self, callback=None):
        self.do_loop(callback)
