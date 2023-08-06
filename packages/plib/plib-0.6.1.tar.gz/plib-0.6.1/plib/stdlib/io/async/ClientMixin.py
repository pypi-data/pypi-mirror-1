#!/usr/bin/env python
"""
Module ClientMixin
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous ClientMixin class.
"""

from _async import BaseCommunicator

class ClientMixin(BaseCommunicator):
    """
    Mixin class for async clients; writes data first, then
    reads back the response. Expects a class earlier in the
    MRO to implement the ``handle_read``, ``handle_write``,
    ``read_complete``, and ``write_complete`` methods. Call
    ``client_communicate`` to start the round-trip data
    exchange. Override ``process_data`` to do something with
    the server's reply. Override ``query_done`` if more than
    one round-trip data exchange is desired before closing
    the connection.
    
    Note that this class assumes that it is the "master" async
    communicator class, meaning it is responsible for calling its
    do_loop method to run the async polling loop. For "clients"
    which may not be the "master" communicators, you can either
    call the ``start`` and ``setup_client`` methods explicitly
    (which are sufficient to make the client respond to async
    polling events) or use the ``PersistentMixin`` class instead.
    """
    
    def setup_client(self, client_id=None):
        """
        Derived classes should override to set up the client's
        connection to the server in whatever way is applicable.
        If the client is already connected, no setup is necessary.
        """
        
        pass
    
    def client_communicate(self, data, client_id=None, callback=None):
        """
        Core method to implement client I/O functionality:
        connects to server, then starts the async polling loop.
        If ``client_id is None``, assume that the client is already
        connected to the server and don't try to connect again.
        """
        
        self.start(data)
        if client_id is not None:
            self.setup_client(client_id)
        self.do_loop(callback)
    
    def writable(self):
        return not self.write_complete()
    
    def handle_write(self):
        super(ClientMixin, self).handle_write()
        if self.write_complete():
            self.clear_write()
    
    def readable(self):
        return not (self.writable() or self.read_complete() or self.done)
    
    def handle_read(self):
        super(ClientMixin, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.check_done()
            self.clear_read()
    
    def process_data(self):
        """
        Derived classes should override to process ``self.read_data``
        and determine whether ``query_done`` should return ``True``.
        """
        
        pass
