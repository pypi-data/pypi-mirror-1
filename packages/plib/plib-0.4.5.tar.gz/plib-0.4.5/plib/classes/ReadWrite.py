#!/usr/bin/env python
"""
Module ReadWrite
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ReadWrite class.
"""

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
    
    The intended use case for this mixin is as an alternate
    read/write handler to be patched in with the client
    and server mixins in plib.stdlib.AsyncServer. For
    example, you could use:
    
    from plib.stdlib.AsyncServer import BaseCommunicator, \
        ClientMixin, ServerMixin, BaseRequestHandler
    class ClientCommunicator(ClientMixin, ReadWrite, BaseCommunicator):
        pass
    class AsyncRequestHandler(ServerMixin, ReadWrite, AsyncRequestHandler):
        pass
    
    These classes would then be usable in the same way as
    the default classes of the same names in
    plib.stdlib.AsyncServer.
    """
    
    bufsize = 4096
    
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
        delta = len(self.read_data) - len_read
        if delta > 0:
            received = self.read_data[-delta:]
            if self.read_len < 0: # len(self.read_data) is also 0
                self.read_len, received = self.unformat_buffer(received)
                self.read_data = received
            self.bytes_read += len(received)
    
    def handle_write(self):
        """
        Formats data first if not yet formatted.
        """
        
        if not self.formatted:
            self.write_data = self.format_buffer(self.write_data)
            self.formatted = True
        super(ReadWrite, self).handle_write()
    
    def read_complete(self):
        return (self.read_len > -1) and (self.bytes_read >= self.read_len)
    
    def write_complete(self):
        return not self.write_data
