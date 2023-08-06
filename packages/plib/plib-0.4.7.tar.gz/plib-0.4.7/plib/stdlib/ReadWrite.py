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
super calls
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
    
    terminator = '/r/n'
    terminator_received = False
    
    def clear_data(self):
        super(TerminatorReadWrite, self).clear_data()
        self.terminator_received = False
    
    def handle_read(self):
        super(TerminatorReadWrite, self).handle_read()
        if self.read_data.endswith(self.terminator):
            self.terminator_received = True
            self.read_data = self.read_data[:-len(self.terminator)]
    
    def read_complete(self):
        return self.terminator_received
    
    def handle_write(self):
        if not self.write_data.endswith(self.terminator):
            self.write_data = self.write_data + self.terminator
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
    read_len = -1
    
    def clear_data(self):
        super(ReadWrite, self).clear_data()
        self.formatted = False
        self.read_len = -1
        self.bytes_read = 0
    
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
        return (self.read_len > -1) and (self.bytes_read >= self.read_len)
    
    def handle_write(self):
        """
        Formats data first if not yet formatted.
        """
        
        if not self.formatted:
            self.write_data = self.format_buffer(self.write_data)
            self.formatted = True
        super(ReadWrite, self).handle_write()
