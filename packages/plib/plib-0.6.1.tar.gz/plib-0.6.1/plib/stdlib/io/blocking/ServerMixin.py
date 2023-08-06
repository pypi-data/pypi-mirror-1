#!/usr/bin/env python
"""
Module ServerMixin
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O ServerMixin class.
"""

class ServerMixin(object):
    """
    Simple server-side blocking I/O; reads data first, then
    writes back the response after processing. This base class
    provides simple "echo" functionality--the input is just
    copied to the output with no other processing. Subclasses
    should override ``process_data`` to do something more. Expects
    a class earlier in the MRO to implement the ``handle_read``,
    ``handle_write``, ``read_complete``, and ``write_complete``
    methods.
    """
    
    def server_communicate(self):
        """
        Core method to implement server I/O functionality: read
        data from client, process it, send reply back to client,
        then clear data and check to see if done. Note that if
        ``query_done`` returns ``False``, it should ensure that either
        ``read_complete`` is False (so more data can be read from
        the client) or that there is more data to write; i.e., if
        there is no state change in the object after ``query_done``
        once returns ``False``, it will presumably return ``False``
        again, and the server will block forever in its loop. (The
        default is for ``read_complete`` to be ``False`` after the
        ``clear_data`` method has run, but derived classes that may
        complicate their behavior must be aware of the implications.)
        """
        
        try:
            while 1:
                while not self.read_complete():
                    self.handle_read()
                self.process_data()
                while not self.write_complete():
                    self.handle_write()
                self.clear_data()
                if self.query_done():
                    break
        finally:
            self.close()
    
    def process_data(self):
        """
        Derived classes should override to do more than echo
        data back to the client.
        """
        
        self.start(self.read_data)
    
    def query_done(self):
        """ Default is to shut down after one back and forth exchange. """
        
        return True

