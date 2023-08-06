#!/usr/bin/env python
"""
Module CLIENTSERVER -- Base I/O Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains base classes that implement common
functionality for blocking I/O clients and servers.
"""

class ClientMixin(object):
    """
    Simple blocking I/O client: writes write_data, then
    reads back read_data, processes the read data, then
    clears data and closes. Call the client_communicate
    method to run one "pass" of the write/read/process data
    loop. Override process_data to do something with the
    server's reply; override query_done if more than one
    round-trip data exchange is desired.
    """
    
    def setup_client(self, client_id=None):
        """
        Derived classes should override to set up the client's
        connection to the server in whatever way is applicable.
        (If the client is already connected, no override is
        necessary.)
        """
        pass
    
    def client_communicate(self, data, client_id=None):
        """
        Core method to implement client I/O functionality:
        connects to server, writes data, reads back the reply,
        processes it, then clears the data and checks to see
        if it is done.
        """
        
        self.start(data)
        self.setup_client(client_id)
        while not self.write_complete():
            self.handle_write()
        while not self.read_complete():
            self.handle_read()
        self.process_data()
        self.clear_data()
        if self.query_done():
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

class RequestMixin(object):
    """
    Simple blocking I/O request handler; reads data, processes it,
    writes back the result, then closes. Override process_data to
    generate the reply; override query_done if more than one
    round-trip data exchange is desired.
    """
    
    def server_communicate(self):
        while not self.read_complete():
            self.handle_read()
        self.process_data()
        while not self.write_complete():
            self.handle_write()
        self.clear_data()
    
    def process_data(self):
        """
        Derived classes should override to do more than echo
        data back to the client.
        """
        self.start(self.read_data)
    
    def query_done(self):
        """ Default is to shut down after one back and forth exchange. """
        return True

class ServerMixin(RequestMixin):
    """
    Simple blocking I/O server, adds serve_forever method. This
    server mixin is meant for I/O types (e.g., a serial device)
    that don't spin off a new channel to accept connections from
    clients, as a socket does; for server-side socket I/O, use
    the RequestMixin class instead.
    """
    
    def query_done(self):
        """ Default is to keep running until doomsday. """
        return False
    
    def serve_forever(self):
        try:
            while not self.query_done():
                self.server_communicate()
        finally:
            self.close()
