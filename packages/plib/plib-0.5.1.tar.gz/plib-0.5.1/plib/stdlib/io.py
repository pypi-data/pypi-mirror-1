#!/usr/bin/env python
"""
Module IO -- Base I/O Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a base class that implements common
functionality for all I/O modes (serial vs. socket,
blocking/synchronous vs. non-blocking/asynchronous, etc.).
"""

class BaseData(object):
    """
    Base class for data storage, not intended for direct use but
    provides a single common baseline for the various I/O types,
    including the base implementation of the core methods.
    """
    
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
