#!/usr/bin/env python
"""
Module SocketDispatcher -- Asynchronous Socket I/O
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a basic asynchronous socket I/O
dispatcher.
"""

import socket
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, EPIPE, ECONNRESET, \
    ENOTCONN, ESHUTDOWN, ECONNABORTED, EISCONN, EBADF, errorcode
# FIXME: why won't this work with async sockets?
#from errno import EINTR
#try:
#    from errno import ERESTART # won't work on OS X
#except ImportError:
#    ERESTART = None # safe alternate

from plib.stdlib.io.socket import SocketIOBase

from _async import AsyncBase

class SocketDispatcher(SocketIOBase, AsyncBase):
    """
    Dispatcher class that fixes a number of minor issues
    with asyncore.dispatcher. Key changes:
    
    - Correctly handles the case where a non-blocking connect
      attempt fails; asyncore.dispatcher ends up bailing to
      ``handle_error`` on the first read or write attempt to the
      socket, but aside from being ugly, this doesn't work if
      the dispatcher won't return ``True`` for ``readable`` or
      ``writable`` until it knows the connect has succeeded--it
      will just hang forever in the polling loop--but this class
      spots the socket error and raises an exception so the loop
      exits.
    
    - The ``handle_error`` method is changed to close the socket
      and then re-raise whatever exception caused it to be called
      (much more Pythonic) -- this behavior is inherited from
      ``AsyncBase``.
    
    - The ``handle_close`` method is called from ``close``,
      instead of the reverse (having the method that's intended
      to be a placeholder call a method that needs to always be
      called makes no sense, and the naming is more consistent if
      the "handle" method is the placeholder).
    """
    
    connect_pending = False
    
    def __init__(self, sock=None, map=None):
        AsyncBase.__init__(self, map)
        SocketIOBase.__init__(self, sock)
    
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
    
    def set_socket(self, sock):
        SocketIOBase.set_socket(self, sock)
        sock.setblocking(0)
        self.set_fileobj(sock, self._map)
    
    def accept(self):
        try:
            return self.socket.accept()
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return (None, None)
            else:
                raise
    
    def connect(self, address):
        self.connected = False
        self.connect_pending = False
        err = self.socket.connect_ex(address)
        # FIXME: Add Winsock return values?
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            # The connect will be completed asynchronously, so
            # set a flag to signal that we're waiting
            self.connect_pending = True
            self.closed = False
        elif err in (0, EISCONN):
            self.addr = address
            self.connected = True
            self.closed = False
            self.handle_connect()
        else:
            raise socket.error, (err, errorcode[err])
    
    def check_error(self):
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err:
            # Re-raise the error so the connect aborts
            raise socket.error, (err, errorcode[err])
    
    def check_connect(self):
        if self.connect_pending:
            self.connect_pending = False
            # We're waiting for a connect to be completed
            # asynchronously, so we need to see if it really
            # was completed or if an error occurred
            self.check_error()
            # If we get here, the connect was successful, so
            # fill in the address
            self.addr = self.socket.getpeername()
        
        # Always set this flag since we only get called if
        # it wasn't already set
        self.connected = True
    
    def send(self, data):
        try:
            return self.socket.send(data)
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return 0
            self.close()
            if why[0] in (EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED):
                return 0
            else:
                raise
    
    def recv(self, buffer_size):
        try:
            # NOTE: We do *not* call ``self.close()`` here on a read of
            # zero bytes, for the same reasons we didn't do it in the
            # base socket I/O code in ``plib.stdlib.io.socket``. See
            # the ``_socket`` module in that sub-package for more info.
            return self.socket.recv(buffer_size)
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return ''
            self.close()
            if why[0] in (EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED):
                return ''
            else:
                raise
    
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
        if self.accepting:
            # Should never get a write event, but if we do, throw
            # it away
            return
        else:
            # Getting a write implies that we are connected, so
            # same logic as for handle_read_event above
            if not self.connected:
                self.check_connect()
                self.handle_connect()
            self.handle_write()
    
    def handle_expt_event(self):
        try:
            y1 = self.__class__.handle_expt.im_func
            y2 = AsyncBase.handle_expt.im_func
        except AttributeError:
            y1 = None
            y2 = False
        if y1 is y2:
            self.check_error()
        else:
            self.handle_expt()
    
    def close(self):
        # This is the method that should be called from all the
        # places that call handle_close in asyncore.dispatcher
        self.del_channel()
        
        # The closed flag ensures that we only go through the
        # actual socket close procedure once (assuming it succeeds),
        # even if we are called multiple times from different
        # trigger events; note that calling socket.close() may not
        # throw an exception even if called on an already closed
        # socket, so we can't use the except clause as our test for
        # being already closed
        if not self.closed:
            self.handle_close()
            self.accepting = False
            self.connected = False
            self.connect_pending = False
            try:
                self.socket.close()
                self.closed = True
            except socket.error, why:
                if why[0] in (ENOTCONN, EBADF, EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED):
                    self.closed = True
                else:
                    raise
    
    def handle_accept(self):
        raise NotImplementedError
    
    def handle_connect(self):
        raise NotImplementedError
    
    # FIXME: why doesn't this work with async sockets? (get connection
    # refused every time client does async connect)
    #def do_loop(self, callback=None):
    #    try:
    #        while 1:
    #            try:
    #               # If we get an 'interrupted system call', don't shut
    #                # down, just re-start the loop
    #                async.loop(self.poll_timeout, self._map, callback)
    #            except socket.error, why:
    #                if why[0] in (EINTR, ERESTART):
    #                    continue
    #                else:
    #                    raise
    #    finally:
    #        self.close()
