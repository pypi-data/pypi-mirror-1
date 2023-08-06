#!/usr/bin/env python
"""
Module AsyncSerial -- Asynchronous Serial I/O Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains classes that provide serial I/O
functionality using the base provided in the async
module in this sub-package. Note that this module requires
the pyserial package, available on SourceForge.

Since the most common forms of serial data exchange bound
each "message" with a terminator string, this module also
contains alternate classes using the terminator read/write
support from the ReadWrite module.
"""

from plib.stdlib.pyserial import SerialIO, SerialClientMixin

from plib.stdlib.async import AsyncBase, ClientMixin, ServerMixin, \
    PersistentMixin
from plib.stdlib.ReadWrite import TerminatorReadWrite

class SerialDispatcher(SerialIO, AsyncBase):
    """
    Class to wrap a serial.Serial instance and provide
    asynchronous I/O using the AsyncBase mechanism.
    """
    
    closed = False
    
    def __init__(self, devid=None, map=None):
        AsyncBase.__init__(self, map)
        if devid is not None:
            self.create_port(devid)
        else:
            self.port = None
    
    def create_port(self, devid):
        self.set_port(Serial(devid))
    
    def set_port(self, port, map=None):
        self.port = port
        self.set_fileobj(port, map)
    
    def read(self, size=1):
        return self.port.read(size)
    
    def write(self, data):
        return self.port.write(data)
    
    def close(self):
        AsyncBase.close(self)
        
        # Check closed flag so we only close the port
        # once, even if this method is called multiple
        # times from different trigger events
        if not self.closed:
            self.port.close()
            self.closed = True

class ClientSerialMixin(SerialClientMixin, ClientMixin):
    """
    Mixin class to provide basic asynchronous serial client
    functionality. Call the client_communicate method to
    open a serial device and send data; override the
    process_data method to do something with the reply.
    """
    pass

class SerialClient(ClientSerialMixin, SerialDispatcher):
    """
    Basic asynchronous serial client class. Call the
    client_communicate method to open a serial device
    and send data; override the process_data method to
    do something with the reply.
    """
    pass

class ServerSerialMixin(ServerMixin):
    """
    Asynchronous server-side serial I/O mixin class. Call the
    serve_forever method to run the server. Note that the
    default is to remain open for an unlimited number of
    round-trip data exchanges; override the query_done method
    to determine when the server should close.
    """
    
    def query_done(self):
        return False # override async default
    
    def serve_forever(self, callback=None):
        self.do_loop(callback) # simple alias for API compatibility

class SerialServer(SerialServerMixin, SerialDispatcher):
    """
    Asynchronous serial device I/O server class. Call the
    serve_forever method to run the server. Note that the
    default is to remain open for an unlimited number of
    round-trip data exchanges; override the query_done method
    to determine when the server should close.
    """
    pass

class PersistentSerialMixin(PersistentMixin):
    """
    Mixin class for persistent, full-duplex asynchronous serial
    device I/O. Can be used for both clients and servers.
    """
    pass # TODO: do we need anything here?

class SerialPersistent(PersistentSerialMixin, SerialDispatcher):
    """
    Base class for persistent, full-duplex asynchronous serial
    device I/O. Can be used for both clients and servers.
    """
    pass

class SerialWithTerminator(TerminatorReadWrite, SerialDispatcher):
    """
    Mixin class to add terminator read/write functionality to
    an asynchronous serial I/O dispatcher.
    """
    pass

class SerialClientWithTerminator(ClientSerialtMixin, SerialWithTerminator):
    """
    Serial I/O client with terminator read/write handling. Call
    the client_communicate method to open a serial device
    and send data; override the process_data method to
    do something with the reply.
    """
    pass

class SerialServerWithTerminator(ServerSerialMixin, SerialWithTerminator):
    """
    Serial I/O server with terminator read/write handling. Call
    the serve_forever method to run the server. Note that the
    default is to remain open for an unlimited number of
    round-trip data exchanges; override the query_done method
    to determine when the server should close.
    """
    pass

class SerialPersistentWithTerminator(PersistentSerialMixin, SerialWithTerminator):
    """
    Persistent, full-duplex asynchronous serial device I/O with
    terminator read/write handling. Can be used for both clients
    and servers.
    """
    pass
