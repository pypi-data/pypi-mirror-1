#!/usr/bin/env python
"""
Module BaseData
Sub-Package STDLIB.IO of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the BaseData class, a base class that
implements common baseline data handling functionality for all
I/O modes (serial vs. socket, blocking/synchronous vs.
non-blocking/asynchronous, etc.).
"""

class BaseData(object):
    """
    Base class for data storage, not intended for direct use but
    provides a single common baseline for the various I/O types,
    including the base implementation of the core methods.
    
    The key limitation of this base data handling mechanism is
    that it has no way to detect that an incoming "message" is
    complete except by detecting a closed channel (which is
    assumed whenever the number of bytes read is less than the
    number of bytes requested). This detection mechanism usually
    works only for a single round-trip data exchange (i.e., one
    read and one write). More sophisticated data handling is
    provided by the classes in the ``plib.stdlib.io.data``
    sub-package.
    
    Note also that the ``auto_close`` flag should only be left
    ``True`` if it is desired that the entire channel be closed
    whenever a read of zero bytes is detected, which indicates
    that the other endpoint of the socket has called either ``close``
    or ``shutdown``. For read/write handling strategies that use
    the socket ``shutdown`` method to signal that a client has
    finished sending but can still receive (e.g., see the
    ``ShutdownReadWrite`` class), the ``auto_close`` flag must
    be set to ``False`` for the strategy to work properly.
    """
    
    auto_close = True
    bufsize = 1
    read_data = ""
    read_done = False
    write_data = ""
    
    def start(self, data):
        self.write_data = data
    
    def handle_read(self):
        data = self.dataread(self.bufsize)
        if data:
            self.read_data += data
        if len(data) < self.bufsize:
            self.read_done = True
        if self.auto_close and (len(data) == 0):
            self.close()
    
    def read_complete(self):
        return self.read_done
    
    def clear_read(self):
        self.read_data = ""
        self.read_done = False
    
    def handle_write(self):
        written = self.datawrite(self.write_data)
        self.write_data = self.write_data[written:]
    
    def write_complete(self):
        return not self.write_data
    
    def clear_write(self):
        self.write_data = ""
    
    def clear_data(self):
        self.clear_read()
        self.clear_write()
    
    # Placeholders that must be implemented by derived classes
    
    def dataread(self, bufsize):
        """ Read up to bufsize bytes of data, return data read. """
        raise NotImplementedError
    
    def datawrite(self, data):
        """ Try to write data, return number of bytes written. """
        raise NotImplementedError
