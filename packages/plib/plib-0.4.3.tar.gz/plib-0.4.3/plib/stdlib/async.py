#!/usr/bin/env python
"""
Module ASYNC -- Asynchronous Client/Server Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains an asynchronous dispatcher class
thats build on the asyncore module in the Python standard
library but fixes a number of minor issues. (Note that one
of the issues is that asyncore.dispatcher is not a new-style
class, meaning that super doesn't work with it; since we
will want to use super in classes that build on this one,
we need to make it new-style.)
"""

import os
import asyncore
import socket
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EISCONN, errorcode

class BaseDispatcher(object):
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
    
    debug = False
    connected = False
    accepting = False
    closing = False
    addr = None
    
    poll_timeout = 1.0
    connect_pending = False
    
    def __init__(self, sock=None, map=None):
        if map is None:
            self._map = asyncore.socket_map
        else:
            self._map = map
        
        if sock:
            self.set_socket(sock, map)
            try:
                self.addr = sock.getpeername()
            except socket.error:
                pass
        else:
            self.socket = None
    
    def __repr__(self):
        status = [self.__class__.__module__ + "." + self.__class__.__name__]
        if self.accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        return '<%s at %#x>' % (' '.join(status), id(self))
    
    def add_channel(self, map=None):
        #self.log_info('adding channel %s' % self)
        if map is None:
            map = self._map
        map[self._fileno] = self
    
    def del_channel(self, map=None):
        fd = self._fileno
        if map is None:
            map = self._map
        if map.has_key(fd):
            #self.log_info('closing channel %d:%s' % (fd, self))
            del map[fd]
        self._fileno = None
    
    def create_socket(self, family, type):
        self.set_socket(socket.socket(family, type))
    
    def set_socket(self, sock, map=None):
        self.socket = sock
        self.socket.setblocking(0)
        self._fileno = sock.fileno()
        self.add_channel(map)
    
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
        self.del_channel()
        self.socket.close()
        self.connected = False
        self.connect_pending = False
        self.handle_close()
    
    def readable(self):
        return True
    
    def writable(self):
        return True
    
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
    
    def handle_expt_event(self):
        self.handle_expt()
    
    def handle_error(self):
        self.close() # eliminate the messy traceback stuff
        raise # and let the exception propagate
    
    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    def __getattr__(self, attr):
        return getattr(self.socket, attr)
    
    def log_info(self, message, type='info'):
        if self.debug or (type != 'info'):
            print '%s: %s' % (type, message)
    
    def handle_expt(self):
        # This corrects the log_info description (asyncore.dispatcher
        # says 'exception' which isn't correct)
        self.log_info('unhandled out of band data', 'warning')
    
    def handle_read(self):
        self.log_info('unhandled read event', 'warning')
    
    def handle_write(self):
        self.log_info('unhandled write event', 'warning')
    
    def handle_connect(self):
        self.log_info('unhandled connect event', 'warning')
    
    def handle_accept(self):
        self.log_info('unhandled accept event', 'warning')
    
    def handle_close(self):
        # This gets called _from_ close(), not the other way around,
        # so eliminate the close() call here
        self.log_info('unhandled close event', 'warning')
    
    def do_loop(self, callback=None):
        """
        Convenience looping method that allows a callback function
        to be called on each iteration of the polling loop. Note that
        we allow the callback to break us out of the loop by returning
        False (not just any false value, but the specific object False).
        """
        
        if callback:
            map = self._map #asyncore.socket_map
            fn = asyncore.poll
            t = self.poll_timeout
            while map and (callback() is not False):
                fn(t, map)
        else:
            # Don't need shorter timeout here since there's no callback
            asyncore.loop(map=self._map)
