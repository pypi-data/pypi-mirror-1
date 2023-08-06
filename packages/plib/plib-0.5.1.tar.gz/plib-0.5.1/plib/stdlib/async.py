#!/usr/bin/env python
"""
Module ASYNC -- Asynchronous Client/Server Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains base classes for asynchronous I/O
functionality. The idea is the same as the asyncore module
in the Python standard library, but the core is abstracted
out so it can be used with various I/O types, not just
network sockets. The specialization to network sockets is
done in the AsyncServer module; AsyncServer.BaseDispatcher
is basically the functional equivalent of asyncore.dispatcher
(but with some fixes to minor issues as noted in the class
docstring). An example of the usage of this module with a
different I/O type is the SerialIO module.

There is also a modified asynchronous loop function that
allows a callback on every iteration, which is useful if a
separate event loop needs to be kept running in parallel
with the async loop (for example, a GUI event loop).
"""

import asyncore
import select

from plib.stdlib.coll import fifo

use_poll = True # make this a global since it shouldn't change much

def loop(timeout=30.0, map=None, callback=None, count=None):
    """
    Basic asynchronous polling loop. Allows a callback function
    to run on each loop iteration; if the callback returns False,
    breaks out of the loop.
    """
    
    if map is None:
        map = asyncore.socket_map
    
    if use_poll and hasattr(select, 'poll'):
        poll_fun = asyncore.poll2
    else:
        poll_fun = asyncore.poll
    
    if count is None:
        if callback is None:
            while map:
                poll_fun(timeout, map)
        else:
            while map and (callback() is not False):
                poll_fun(timeout, map)
    
    else:
        if callback is None:
            while map and count > 0:
                poll_fun(timeout, map)
                count = count - 1
        else:
            while map and (count > 0) and (callback() is not False):
                poll_fun(timeout, map)
                count = count - 1

class AsyncBase(object):
    """
    Base class that abstracts out the core functionality
    for asynchronous I/O. Can be used to wrap any object
    that has a Unix file descriptor; the set_fileobj
    method must be called with the object to be wrapped.
    Note that this class does *not* set file descriptors
    to non-blocking mode; that can't be reliably done
    here because there are too many different types of
    descriptors. Thus, users of this class must first set
    their file descriptors to non-blocking mode before
    calling the set_fileobj method.
    
    This class also allows a callback function on
    each iteration of the polling loop. This allows other
    processing to be done while waiting for I/O (one
    common use case would be keeping a GUI event loop
    running concurrently with the network polling loop).
    """
    
    debug = False
    poll_timeout = 1.0
    
    def __init__(self, map=None):
        if map is None:
            self._map = asyncore.socket_map
        else:
            self._map = map
        self._fileno = None
    
    def __repr__(self):
        status = [self.__class__.__module__ + "." + self.__class__.__name__]
        self.repr_status(status)
        return '<%s at %#x>' % (' '.join(status), id(self))
    
    def repr_status(self):
        pass # derived classes can add more stuff to repr here
    
    def set_fileobj(self, obj, map=None):
        self._fileno = obj.fileno()
        self.add_channel(map)
    
    def add_channel(self, map=None):
        if map is None:
            map = self._map
        map[self._fileno] = self
    
    def del_channel(self, map=None):
        fd = self._fileno
        if fd is not None:
            if map is None:
                map = self._map
            if map.has_key(fd):
                del map[fd]
            self._fileno = None
    
    def close(self):
        self.del_channel()
        self.handle_close()
    
    def readable(self):
        return True
    
    def writable(self):
        return True
    
    def handle_read_event(self):
        self.handle_read()
    
    def handle_write_event(self):
        self.handle_write()
    
    def handle_expt_event(self):
        self.handle_expt()
    
    def handle_error(self):
        self.close()
        raise
    
    def handle_expt(self):
        raise NotImplementedError
    
    def handle_read(self):
        raise NotImplementedError
    
    def handle_write(self):
        raise NotImplementedError
    
    def handle_close(self):
        raise NotImplementedError
    
    def do_loop(self, callback=None):
        """
        Convenience looping method that allows a callback function
        to be called on each iteration of the polling loop. Note that
        we allow the callback to break us out of the loop by returning
        False (not just any false value, but the specific object False).
        """
        
        try:
            loop(self.poll_timeout, self._map, callback)
        finally:
            self.close()

class BaseCommunicator(object):
    """
    Base class for async communicator mixins. Expects a class earlier
    in the MRO to implement the clear_data method.
    """
    
    done = False
    
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
        and self.read_data have each been processed once). Once this
        method returns, the data fields will be cleared, so any
        processing based on them must be completed before this
        method is called.
        """
        
        if self.query_done():
            self.done = True
            self.close()

class ClientMixin(BaseCommunicator):
    """
    Mixin class for async clients; writes data first, then
    reads back the response. Expects a class earlier in the
    MRO to implement the handle_read, handle_write, read_complete,
    and write_complete methods. Call client_communicate to start
    the round-trip data exchange. Override process_data to do
    something with the server's reply. Override query_done if
    more than one round-trip data exchange is desired before
    closing the connection.
    
    Note that this class assumes that it is the "master" async
    communicator class, meaning it is responsible for calling its
    do_loop method to run the async polling loop. For "clients"
    which are not the "master" communicators, you can either call
    the start and setup_client methods explicitly (which are
    sufficient to make the client respond to async polling events)
    or use the PersistentMixin class below instead.
    """
    
    def setup_client(self, client_id=None):
        """
        Derived classes should override to set up the client's
        connection to the server in whatever way is applicable.
        (If the client is already connected, no override is
        necessary.)
        """
        pass
    
    def client_communicate(self, data, client_id=None, callback=None):
        """
        Core method to implement client I/O functionality:
        connects to server, then starts the async polling loop.
        """
        
        self.start(data)
        self.setup_client(client_id)
        self.do_loop(callback)
    
    def writable(self):
        return not self.write_complete()
    
    def readable(self):
        return not (self.writable() or self.read_complete() or self.done)
    
    def handle_read(self):
        super(ClientMixin, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.check_done()
    
    def process_data(self):
        """
        Derived classes should override to process self.read_data
        and determine whether query_done should return True.
        """
        pass

class ServerMixin(BaseCommunicator):
    """
    Mixin for server-side programs; reads data first, then
    writes back the response after processing. This base class
    provides simple "echo" functionality--the input is just
    copied to the output with no other processing. Subclasses
    should override process_data to do something more. Expects
    a class earlier in the MRO to implement the handle_read,
    handle_write, read_complete, and write_complete methods.
    """
    
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
        self.start(self.read_data)

class PersistentMixin(BaseCommunicator):
    """
    Mixin for both client and server side communicators that want
    to maintain a persistent, full-duplex connection (i.e., instead
    of a write/read or read/write loop and then a check for done,
    always be ready to read, and write whenever you have something
    to write, and never being "done" by default (you have to override
    query_done to check for possible "done" conditions here). Expects
    a class earlier in the MRO to implement the handle_read, handle_write,
    read_complete, write_complete, clear_read, and clear_write methods.
    
    Note that, because reads and writes may overlap, this class also
    implements a simple queue for write data to ensure that all data
    gets written in the correct order and none is clobbered; to make this
    work, a class earlier in the MRO must also implement the start method.
    Also, the reading and writing fields are added to ensure that once a
    read or write is started, it must complete before another operation
    can start.
    """
    
    data_queue = None
    reading = False
    writing = False
    
    def writable(self):
        return not (self.reading or self.write_complete() or self.done)
    
    def start(self, data):
        if self.write_complete():
            super(PersistentMixin, self).start(data)
        else:
            if self.data_queue is None:
                self.data_queue = fifo()
            self.data_queue.append(data)
    
    def handle_write(self):
        self.writing = True
        super(PersistentMixin, self).handle_write()
        if self.write_complete():
            self.check_done()
            self.clear_write()
            self.writing = False
            if (not self.done) and self.data_queue:
                super(PersistentMixin, self).start(self.data_queue.next())
    
    def readable(self):
        return not (self.writing or self.done)
    
    def handle_read(self):
        self.reading = True
        super(PersistentMixin, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.check_done()
            self.clear_read()
            self.reading = False
    
    def process_data(self):
        """
        Derived classes should override to process self.read_data
        and determine whether query_done should return True.
        """
        pass
    
    def query_done(self):
        """
        Derived classes should override to check for conditions where
        we should be done and close ourselves.
        """
        return False
