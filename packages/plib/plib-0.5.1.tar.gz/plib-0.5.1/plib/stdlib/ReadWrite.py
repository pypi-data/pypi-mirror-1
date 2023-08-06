#!/usr/bin/env python
"""
Module ReadWrite -- I/O read/write and formatting classes
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains classes that provide various ways
of handling read/write of data for I/O. These are all
mixin classes that are intended to overlay the baseline
functionality of an I/O class such as those in the
AsyncServer or SerialIO modules. Thus, all classes use
super calls to do the actual work, then post-process the
results as necessary.
"""

class TerminatorReadWrite(object):
    """
    Mixin I/O class that looks for a terminator to determine
    when a read is complete and should be processed. Simpler
    than the formatted ReadWrite class below, but more limited
    in usefulness. Strips the terminator from self.read_data
    once detected, and adds the terminator to self.write_data
    before writing it.
    """
    
    overflow = ""
    terminator = '\r\n'
    terminator_received = False
    terminator_written = False
    
    def clear_read(self):
        """
        After clearing, checks for overflow data and puts
        it back into the processing queue if present. Note
        that this method may be called recursively if overflow
        data is present.
        """
        
        super(TerminatorReadWrite, self).clear_read()
        self.terminator_received = False
        if self.overflow:
            self.read_data = self.overflow
            self.overflow = ""
            self.check_terminator()
        if self.read_complete():
            self.process_data()
            self.check_done()
            self.clear_read()
    
    def check_terminator(self):
        """
        Checks for terminator in read data, and stores away any
        overflow data temporarily.
        """
        
        if self.terminator in self.read_data:
            self.terminator_received = True
            self.read_data, self.overflow = self.read_data.split(self.terminator, 1)
    
    def handle_read(self):
        """
        Checks incoming data for terminator.
        """
        
        super(TerminatorReadWrite, self).handle_read()
        self.check_terminator()
    
    def read_complete(self):
        return self.terminator_received
    
    def clear_write(self):
        super(TerminatorReadWrite, self).clear_write()
        self.terminator_written = False
    
    def handle_write(self):
        """
        Adds terminator to the end of each package of written data.
        """
        
        if not self.terminator_written:
            self.write_data = self.write_data + self.terminator
            self.terminator_written = True
        super(TerminatorReadWrite, self).handle_write()

class ReadWrite(object):
    """
    Mixin read/write class that converts back and forth
    between simple string data and formatted data that
    has the content length in front. When writing, it
    takes self.write_data and formats it as below; when
    reading, it assumes the incoming data is formatted
    as below and extracts the content into self.read_data.
    (Note that the read_data and write_data fields may be
    clobbered at any time, so data that needs to be static
    should be duplicate stored in another variable.)
    
    Data format: <content-length>\r\n<content>
    """
    
    bytes_read = 0
    formatted = False
    overflow = ""
    read_len = -1
    
    def clear_read(self):
        """
        After clearing, checks for overflow data and puts
        it back into the processing queue if present. Note
        that this method may be called recursively if overflow
        data is present.
        """
        
        super(ReadWrite, self).clear_read()
        self.read_len = -1
        self.bytes_read = 0
        if self.overflow:
            self.read_len, self.read_data = self.unformat_buffer(self.overflow)
            self.overflow = ""
            self.bytes_read = len(self.read_data)
        if self.read_complete():
            self.process_data()
            self.check_done()
            self.clear_read()
    
    def clear_write(self):
        super(ReadWrite, self).clear_write()
        self.formatted = False
    
    def format_buffer(self, data):
        """ Encodes data length at front of data. """
        
        return "%s\r\n%s" % (str(len(data)), data)
    
    def unformat_buffer(self, data):
        """ Splits encoded data into length and content. """
        
        lstr, received = data.split("\r\n", 1)
        return int(lstr), received
    
    def handle_read(self):
        """
        Unformats incoming data first if content length not yet
        extracted.
        """
        
        len_read = len(self.read_data)
        super(ReadWrite, self).handle_read()
        if len(self.read_data) > len_read:
            if self.read_len < 0: # len(self.read_data) is also 0
                self.read_len, received = self.unformat_buffer(self.read_data)
                self.read_data = received
            self.bytes_read += (len(self.read_data) - len_read)
    
    def read_complete(self):
        """
        Checks for overflow data and stores it away temporarily.
        """
        
        if self.read_len < 0:
            return False
        overflow_len = self.bytes_read - self.read_len
        if overflow_len > 0:
            self.overflow = self.read_data[-overflow_len:]
            self.read_data = self.read_data[:self.read_len]
            self.bytes_read -= overflow_len
        return (self.bytes_read >= self.read_len)
    
    def handle_write(self):
        """
        Formats data first if not yet formatted.
        """
        
        if not self.formatted:
            self.write_data = self.format_buffer(self.write_data)
            self.formatted = True
        super(ReadWrite, self).handle_write()
