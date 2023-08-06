#!/usr/bin/env python
"""
Module ReadWriteMonitor
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ReadWriteMonitor class. This is
a useful class for testing client/server I/O channels; it
prints notification of all significant read/write method
calls to standard output.
"""

class ReadWriteMonitor(object):
    
    def readable(self):
        result = super(ReadWriteMonitor, self).readable()
        print "%s readable: %s" % (self.__class__.__name__, result)
        return result
    
    def handle_read(self):
        print "%s read data %s" % (self.__class__.__name__, self.read_data)
        super(ReadWriteMonitor, self).handle_read()
        print "%s read data %s" % (self.__class__.__name__, self.read_data)
    
    def process_data(self):
        print "%s processing data %s" % (self.__class__.__name__, self.read_data)
        super(ReadWriteMonitor, self).process_data()
    
    def clear_read(self):
        print "%s clearing read data" % self.__class__.__name__
        super(ReadWriteMonitor, self).clear_read()
    
    def writable(self):
        result = super(ReadWriteMonitor, self).writable()
        print "%s writable: %s" % (self.__class__.__name__, result)
        return result
    
    def handle_write(self):
        print "%s write data %s" % (self.__class__.__name__, self.write_data)
        super(ReadWriteMonitor, self).handle_write()
        print "%s write data %s" % (self.__class__.__name__, self.write_data)
    
    def clear_write(self):
        print "%s clearing write data" % self.__class__.__name__
        super(ReadWriteMonitor, self).clear_write()
