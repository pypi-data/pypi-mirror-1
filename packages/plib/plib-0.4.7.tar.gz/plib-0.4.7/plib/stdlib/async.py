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

use_poll = False # make this a global since it shouldn't change much

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
    
    def close(self):
        self.del_channel()
    
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
        self.close() # no messy tracebacks here
        raise # and let the exception propagate
    
    def handle_expt(self):
        raise NotImplementedError
    
    def handle_read(self):
        raise NotImplementedError
    
    def handle_write(self):
        raise NotImplementedError
    
    def do_loop(self, callback=None):
        """
        Convenience looping method that allows a callback function
        to be called on each iteration of the polling loop. Note that
        we allow the callback to break us out of the loop by returning
        False (not just any false value, but the specific object False).
        """
        
        loop(self.poll_timeout, self._map, callback)

class BaseData(object):
    """
    Base class for data storage, not intended for direct use but
    provides a single common baseline for the various I/O types,
    including the base implementation of the clear_data method.
    """
    
    read_data = ""
    write_data = ""
    
    def clear_data(self):
        self.read_data = ""
        self.write_data = ""

class BaseCommunicator(object):
    """
    Basic async communicator mixin class; can be overlaid on any
    class derived from AsyncBase to provide read/write data buffers
    and checking of completion status. Expects a class earlier in
    the MRO to implement the clear_data method.
    """
    
    done = False
    
    def query_done(self):
        """
        Should return True if no further read/write operations
        are necessary. Default is to always return True, which
        means that as soon as self.write_data and self.read_data
        have both been processed once, we are done and the object
        will close. Note that if this method returns False, it
        should set up the object properly to be either readable
        or writable before returning (otherwise the object will
        be present in the async loop but "orphaned" because it is
        receiving no events); often, this can be done by simply
        calling clear_data, but not always (which is why this call
        is not hard-coded here).
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
    Mixin class for client programs; writes data first, then
    reads back the response. If this is the "master" communicator
    object in your program, its do_loop method can be called to
    run the async polling loop. Expects a class earlier in the
    MRO to implement the handle_read, handle_write, read_complete,
    and write_complete methods.
    """
    
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
        self.write_data = self.read_data
