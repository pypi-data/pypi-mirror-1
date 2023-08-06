#!/usr/bin/env python
"""
Module ClientMixin
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O ClientMixin class.
"""

class ClientMixin(object):
    """
    Simple blocking I/O client: writes ``write_data``, then
    reads back ``read_data``, processes the read data, then
    clears data and closes. Call the ``client_communicate``
    method to run one "pass" of the write/read/process data
    loop. Override ``process_data`` to do something with the
    server's reply; override ``query_done`` if more than one
    round-trip data exchange is desired.
    """
    
    def setup_client(self, client_id=None):
        """
        Derived classes should override to set up the client's
        connection to the server in whatever way is applicable.
        If the client is already connected, no setup is necessary.
        """
        
        pass
    
    def client_communicate(self, data, client_id=None):
        """
        Core method to implement client I/O functionality:
        connects to server, writes data, reads back the reply,
        processes it, then clears the data and checks to see
        if it is done. Note that if ``query_done`` returns False,
        it should either call the ``start`` method to supply
        more data to be written, or ensure that ``write_complete``
        is ``True``; otherwise the client will block forever in
        the ``while not self.write_complete()`` loop.
        
        Also note that if ``client_id is None``, we assume that
        the client is already connected to the server and don't
        try to connect again.
        """
        
        try:
            self.start(data)
            if client_id is not None:
                self.setup_client(client_id)
            while 1:
                while not self.write_complete():
                    self.handle_write()
                while not self.read_complete():
                    self.handle_read()
                self.process_data()
                self.clear_data()
                if self.query_done():
                    break
        finally:
            self.close()
    
    def process_data(self):
        """
        Derived classes should override to do something with the
        data read back from the server.
        """
        
        pass
    
    def query_done(self):
        """ Default is to shut down after one back and forth exchange. """
        
        return True
