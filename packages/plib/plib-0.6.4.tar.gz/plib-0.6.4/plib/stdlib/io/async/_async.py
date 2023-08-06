#!/usr/bin/env python
"""
Module ASYNC -- Asynchronous I/O Utilities
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the base class for asynchronous I/O
functionality. The idea is the same as the asyncore module
in the Python standard library, but the core is abstracted
out so it can be used with various I/O types, not just
network sockets.

There is also a modified asynchronous loop function that
allows a callback on every iteration, which is useful if a
separate event loop needs to be kept running in parallel
with the async loop (for example, a GUI event loop).
"""

import asyncore
import select

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
    that has a Unix file descriptor; the ``set_fileobj``
    method must be called with the object to be wrapped.
    Note that this class does *not* set file descriptors
    to non-blocking mode; that can't be reliably done
    here because there are too many different types of
    descriptors. Thus, users of this class must first set
    their file descriptors to non-blocking mode before
    calling the ``set_fileobj`` method.
    
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
    
    def repr_status(self, status):
        pass # derived classes can add more stuff to repr here
    
    def fileno(self):
        return self._fileno # so we look file-like
    
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
    Base class for async communicator mixins.
    """
    
    done = False
    
    def query_done(self):
        """
        Should return ``True`` if no further read/write operations
        are necessary. Default is to always return ``True``, which
        means that as soon as ``self.write_data`` and ``self.read_data``
        have both been processed once, we are done and the object
        will close.
        """
        
        return True
    
    def check_done(self):
        """
        This method is intended to be called whenever a single "pass"
        of the read/write cycle completes (i.e., ``self.write_data``
        and ``self.read_data`` have each been processed once). Once
        this method returns, the data fields will be cleared, so any
        processing based on them must be completed before this
        method is called.
        """
        
        if self.query_done():
            self.done = True
            self.close()
