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

import socket
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, ECONNABORTED, EISCONN, EBADF, errorcode

from plib.stdlib.async import AsyncBase, ClientMixin, ServerMixin, \
    PersistentMixin
from plib.stdlib.socketio import SocketIO, ConnectMixin, SocketClientMixin

class BaseDispatcher(SocketIO, AsyncBase):
    """
    Dispatcher class that fixes a number of minor issues
    with asyncore.dispatcher. Key changes:
    
    -- correctly handles the case where a non-blocking connect
       attempt fails; asyncore.dispatcher ends up bailing to
       handle_error on the first read or write attempt to the
       socket, but aside from being ugly, this doesn't work if
       the dispatcher won't return True for readable or writable
       until it knows the connect has succeeded--it will just
       hang forever in the polling loop--but this class spots
       the socket error and raises an exception so the loop exits.
    
    -- handle_error is changed to close the socket and then
       re-raise whatever exception caused it to be called
       (much more Pythonic) -- this behavior is inherited
       from AsyncBase
    
    -- handle_close is called from close, instead of the
       reverse (having the method that's intended to be
       a placeholder call a method that needs to always be
       called makes no sense)
    """
    
    connect_pending = False
    
    def __init__(self, sock=None, map=None):
        AsyncBase.__init__(self, map)
        SocketIO.__init__(self, sock)
        # TODO: should we call handle_connect here if sock is connected?
    
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
        SocketIO.set_socket(self, sock)
        self.socket.setblocking(0)
        self.set_fileobj(sock, self._map)
    
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
            y2 = dispatcher.handle_expt.im_func
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
                if why[0] in (ENOTCONN, EBADF):
                    self.closed = True
                else:
                    raise
    
    def handle_accept(self):
        raise NotImplementedError
    
    def handle_connect(self):
        raise NotImplementedError

class BaseSocket(BaseDispatcher):
    """
    Socket async I/O class with defaults for events that don't need handlers.
    """
    
    def handle_connect(self):
        pass # don't need any warning here
    
    def handle_expt(self):
        pass # ignore any out of band data
    
    def handle_close(self):
        pass # don't need any warning here

class AsyncConnectMixin(object):
    """
    Mixin class to enable async client connect functionality by
    overriding the writable and readable methods to return True
    if a connect is pending (to make sure we get notified when
    the asynchronous connect completes; it could be either a
    read or a write select() return so we allow for both to be safe).
    """
    
    def writable(self):
        return self.connect_pending or super(AsyncConnectMixin, self).writable()
    
    def readable(self):
        return self.connect_pending or super(AsyncConnectMixin, self).readable()

class ClientSocketMixin(AsyncConnectMixin, SocketClientMixin, ClientMixin):
    """
    Mixin class to provide basic asynchronous socket client
    functionality. Call the client_communicate method to
    connect to a server and send data; override the
    process_data method to do something with the reply.
    """
    pass

class ClientCommunicator(ClientSocketMixin, BaseSocket):
    """
    Basic asynchronous socket client class. Call the
    client_communicate method to connect to a server
    and send data; override the process_data method to
    do something with the reply.
    """
    pass

class ServerSocketMixin(ServerMixin):
    """
    Asynchronous server-side socket I/O mixin class. Main usage
    is as a mixin for the request handler.
    """
    pass # TODO: do we need anything here?

class ServerCommunicator(ServerSocketMixin, BaseSocket):
    """
    Asynchronous I/O socket server class. Mainly useful for
    wrapping socket objects provided by other means; for most
    normal socket server applications, use AsyncRequestHandler
    and ServerDispatcher.
    """
    pass

class PersistentSocketMixin(AsyncConnectMixin, ConnectMixin, PersistentMixin):
    """
    Mixin class for persistent, full-duplex asynchronous socket
    I/O. Can be used for both clients and servers.
    """
    pass

class PersistentCommunicator(PersistentSocketMixin, BaseSocket):
    """
    Base class for persistent, full-duplex asynchronous socket
    I/O. Can be used for both clients and servers.
    """
    pass

class BaseRequestHandler(BaseSocket):
    """
    Socket dispatcher class set up to serve as a request handler.
    """
    
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        BaseSocket.__init__(self, request)

class AsyncRequestHandler(ServerSocketMixin, BaseRequestHandler):
    """
    Base class for asynchronous socket request handler; default is
    to do one round-trip data exchange and then shut down.
    """
    pass

class PersistentRequestHandler(PersistentMixin, BaseRequestHandler):
    """
    Base class for persistent, full-duplex asynchronous socket
    request handler.
    """
    pass # NOTE: don't need the additional ConnectMixin functionality for a request handler

class ServerDispatcher(BaseDispatcher):
    """
    Class for the actual server; dispatches an instance of
    its communicator class to handle each request. Pretty much
    a functional equivalent to SocketServer but using async I/O
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
    
    def close(self):
        BaseDispatcher.close(self)
        self.server_close()
    
    def server_close(self):
        """ Placeholder for derived classes. """
        pass
    
    def handle_close(self):
        pass # don't need any warning here
    
    def handle_accept(self):
        conn, addr = self.accept()
        self.handler(conn, addr, self)
    
    def serve_forever(self, callback=None):
        self.do_loop(callback) # simple alias for API compatibility
