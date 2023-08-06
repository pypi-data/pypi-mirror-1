#!/usr/bin/env python
"""
Module ReadWriteMonitor
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ReadWriteMonitor class. This is
a useful class for testing client/server I/O channels; it
prints notification of all significant read/write method
calls to standard output.
"""

class ReadWriteMonitor(object):
    
    def handle_connect(self):
        print "%s handling connect" % self.__class__.__name__
        super(ReadWriteMonitor, self).handle_connect()
    
    def readable(self):
        result = super(ReadWriteMonitor, self).readable()
        print "%s readable: %s" % (self.__class__.__name__, result)
        return result
    
    def handle_read(self):
        print "%s read data %r" % (self.__class__.__name__, self.read_data)
        if hasattr(self, 'terminator_received'):
            print "%s terminator received: %s" % (self.__class__.__name__, self.terminator_received)
        if hasattr(self, 'read_len'):
            print "%s bytes expected: %s" % (self.__class__.__name__, self.read_len)
        if hasattr(self, 'bytes_read'):
            print "%s bytes read: %s" % (self.__class__.__name__, self.bytes_read)
        super(ReadWriteMonitor, self).handle_read()
        print "%s read data %r" % (self.__class__.__name__, self.read_data)
        if hasattr(self, 'terminator_received'):
            print "%s terminator received: %s" % (self.__class__.__name__, self.terminator_received)
        if hasattr(self, 'read_len'):
            print "%s bytes expected: %s" % (self.__class__.__name__, self.read_len)
        if hasattr(self, 'bytes_read'):
            print "%s bytes read: %s" % (self.__class__.__name__, self.bytes_read)
    
    def read_complete(self):
        result = super(ReadWriteMonitor, self).read_complete()
        print "%s read complete: %s" % (self.__class__.__name__, result)
        return result
    
    def process_data(self):
        print "%s processing data %r" % (self.__class__.__name__, self.read_data)
        super(ReadWriteMonitor, self).process_data()
    
    def clear_read(self):
        if hasattr(self, 'terminator_received'):
            print "%s terminator received: %s" % (self.__class__.__name__, self.terminator_received)
        if hasattr(self, 'read_len'):
            print "%s bytes expected: %s" % (self.__class__.__name__, self.read_len)
        if hasattr(self, 'bytes_read'):
            print "%s bytes read: %s" % (self.__class__.__name__, self.bytes_read)
        print "%s clearing read data" % self.__class__.__name__
        super(ReadWriteMonitor, self).clear_read()
        if hasattr(self, 'terminator_received'):
            print "%s terminator received: %s" % (self.__class__.__name__, self.terminator_received)
        if hasattr(self, 'read_len'):
            print "%s bytes expected: %s" % (self.__class__.__name__, self.read_len)
        if hasattr(self, 'bytes_read'):
            print "%s bytes read: %s" % (self.__class__.__name__, self.bytes_read)
    
    def start(self, data):
        print "%s starting data %r" % (self.__class__.__name__, data)
        super(ReadWriteMonitor, self).start(data)
    
    def writable(self):
        result = super(ReadWriteMonitor, self).writable()
        print "%s writable: %s" % (self.__class__.__name__, result)
        return result
    
    def handle_write(self):
        print "%s write data %r" % (self.__class__.__name__, self.write_data)
        if hasattr(self, 'terminator_written'):
            print "%s terminator written: %s" % (self.__class__.__name__, self.terminator_written)
        if hasattr(self, 'formatted'):
            print "%s formatted: %s" % (self.__class__.__name__, self.formatted)
        super(ReadWriteMonitor, self).handle_write()
        print "%s write data %r" % (self.__class__.__name__, self.write_data)
        if hasattr(self, 'terminator_written'):
            print "%s terminator written: %s" % (self.__class__.__name__, self.terminator_written)
        if hasattr(self, 'formatted'):
            print "%s formatted: %s" % (self.__class__.__name__, self.formatted)
    
    def write_complete(self):
        result = super(ReadWriteMonitor, self).write_complete()
        print "%s write complete: %s" % (self.__class__.__name__, result)
        return result
    
    def clear_write(self):
        if hasattr(self, 'terminator_written'):
            print "%s terminator written: %s" % (self.__class__.__name__, self.terminator_written)
        if hasattr(self, 'formatted'):
            print "%s formatted: %s" % (self.__class__.__name__, self.formatted)
        print "%s clearing write data" % self.__class__.__name__
        super(ReadWriteMonitor, self).clear_write()
        if hasattr(self, 'terminator_written'):
            print "%s terminator written: %s" % (self.__class__.__name__, self.terminator_written)
        if hasattr(self, 'formatted'):
            print "%s formatted: %s" % (self.__class__.__name__, self.formatted)
    
    def handle_error(self):
        print "%s handling error" % self.__class__.__name__
        super(ReadWriteMonitor, self).handle_error()
    
    def handle_close(self):
        print "%s handling close" % self.__class__.__name__
        super(ReadWriteMonitor, self).handle_close()
