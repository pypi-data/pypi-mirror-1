#!/usr/bin/env python
"""
Module ShutdownReadWrite
Sub-Package STDLIB.IO.DATA of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ShutdownReadWrite alternate data
handling class.
"""

import socket

class ShutdownReadWrite(object):
    """
    Mixin read/write class that calls ``shutdown`` on its socket
    when it is finished writing, and detects the end of data
    being read by the read end of the socket closing (which
    is signalled by a read of zero bytes). Obviously, this
    method only works for a single round-trip data exchange;
    hence, the ``clear_read`` and ``clear_write`` methods are
    not overridden. Also, this method is only designed to work
    with sockets; hence, the ``shutdown`` method assumes that
    the socket instance variable contains a socket.
    
    Note that the ``auto_close`` class field here is set to
    ``False`` (which means that this class must come *before*
    the ``BaseData`` class in the MRO), so that the channel will
    not automatically be closed when a read of zero bytes is
    detected. This is so that the ``shutdown`` method strategy
    described above will work properly (since it requires that
    each endpoint shut itself down separately, instead of the
    entire channel being closed at once).
    """
    
    auto_close = False
    shutdown_received = False
    write_started = False
    
    def handle_read(self):
        len_read = len(self.read_data)
        super(ShutdownReadWrite, self).handle_read()
        if len_read == len(self.read_data):
            self.shutdown_received = True
    
    def read_complete(self):
        return self.shutdown_received
    
    def handle_write(self):
        self.write_started = True
        super(ShutdownReadWrite, self).handle_write()
    
    def write_complete(self):
        result = super(ShutdownReadWrite, self).write_complete()
        if result and self.write_started:
            self.shutdown()
            self.write_started = False
        return result
    
    def shutdown(self):
        self.socket.shutdown(socket.SHUT_WR)
