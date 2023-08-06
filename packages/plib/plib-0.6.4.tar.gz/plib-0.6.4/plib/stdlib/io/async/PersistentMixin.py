#!/usr/bin/env python
"""
Module PersistentMixin
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous PersistentMixin class.
"""

from plib.stdlib.coll import fifo

from _async import BaseCommunicator

class PersistentMixin(BaseCommunicator):
    """
    Mixin for both client and server side communicators that want
    to maintain a persistent, full-duplex connection (i.e., instead
    of a write/read or read/write loop and then a check for done,
    always be ready to read, and write whenever you have something
    to write, and never being "done" by default (you have to override
    ``query_done`` to check for possible "done" conditions here). Expects
    a class earlier in the MRO to implement the ``handle_read``,
    ``handle_write``, ``read_complete``, ``write_complete``,
    ``clear_read``, and ``clear_write`` methods.
    
    Note that, because reads and writes may overlap, this class also
    implements a simple queue for write data to ensure that all data
    gets written in the correct order and none is clobbered; to make this
    work, a class earlier in the MRO must also implement the ``start``
    method, which should enable the actual transfer of a single item of
    data. Also, the ``reading`` and ``writing`` fields are added to
    ensure that once a read or write is started, it must complete
    before another operation can start.
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
        Derived classes should override to process ``self.read_data``
        and determine whether ``query_done`` should return ``True``.
        """
        
        pass
    
    def query_done(self):
        """
        Derived classes should override to check for conditions where
        we should be done and close ourselves.
        """
        
        return False
