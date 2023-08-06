#!/usr/bin/env python
"""
Module SerialIO -- Asynchronous Serial I/O Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains classes that provide basic blocking
serial I/O functionality. Note that this module requires
the pyserial package, available on SourceForge.

Since the most common forms of serial data exchange bound
each "message" with a terminator string, this module also
contains alternate classes using the terminator read/write
support from the ReadWrite module.
"""

import os

from plib.stdlib.pyserial import SerialIO, SerialClientMixin
from plib.stdlib.ClientServer import ClientMixin, ServerMixin
from plib.stdlib.ReadWrite import TerminatorReadWrite

class SerialBase(SerialIO):
    """
    Base class for blocking serial I/O.
    """
    
    blocking_mode = True

class ClientSerialMixin(SerialClientMixin, ClientMixin):
    """
    Mixin class to provide basic blocking serial I/O client
    functionality. Call the client_communicate method to
    connect to a server and send data; override the
    process_data method to do something with the reply.
    """
    pass

class SerialClient(ClientSerialMixin, SerialBase):
    """
    Basic blocking serial I/O client class. Call the
    client_communicate method to open a serial device
    and send data; override the process_data method to
    do something with the reply.
    """
    pass

class ServerSerialMixin(ServerMixin):
    """
    Blocking server-side serial I/O mixin class. Call the
    serve_forever method to run the server. Note that the
    default is to remain open for an unlimited number of
    round-trip data exchanges; override the query_done method
    to determine when the server should close.
    """
    pass # TODO: do we need anything here?

class SerialServer(ServerSerialMixin, SerialBase):
    """
    Blocking serial device I/O server class. Call the
    serve_forever method to run the server. Note that the
    default is to remain open for an unlimited number of
    round-trip data exchanges; override the query_done method
    to determine when the server should close.
    """
    pass

class SerialIOWithTerminator(TerminatorReadWrite, SerialBase):
    """
    Mixin class to add terminator read/write functionality to
    a blocking serial I/O channel.
    """
    pass

class SerialClientWithTerminator(ClientSerialMixin, SerialIOWithTerminator):
    """
    Blocking serial I/O client with terminator read/write
    handling. Call the client_communicate method to open a
    serial device and send data; override the process_data
    method to do something with the reply.
    """
    pass

class SerialServerWithTerminator(ServerSerialMixin, SerialIOWithTerminator):
    """
    Blocking serial I/O server with terminator read/write
    handling. Call the serve_forever method to run the server.
    Note that the default is to remain open for an unlimited number
    of round-trip data exchanges; override the query_done method
    to determine when the server should close.
    """
    pass
