#!/usr/bin/env python
"""
Module ServerMixin
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous ServerMixin class.
"""

from _async import BaseCommunicator

class ServerMixin(BaseCommunicator):
    """
    Mixin for server-side programs; reads data first, then
    writes back the response after processing. This base class
    provides simple "echo" functionality--the input is just
    copied to the output with no other processing. Subclasses
    should override ``process_data`` to do something more. Expects
    a class earlier in the MRO to implement the ``handle_read``,
    ``handle_write``, ``read_complete``, and ``write_complete``
    methods.
    """
    
    def readable(self):
        return not (self.writable() or self.read_complete())
    
    def handle_read(self):
        super(ServerMixin, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.clear_read()
    
    def process_data(self):
        """
        Derived classes should override to do something more than
        just echo input to output.
        """
        
        self.start(self.read_data)
    
    def writable(self):
        return not (self.write_complete() or self.done)
    
    def handle_write(self):
        super(ServerMixin, self).handle_write()
        if self.write_complete():
            self.check_done()
            self.clear_write()
