#!/usr/bin/env python
"""
Module SOCKETCLIENT -- Client Socket Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements a basic blocking socket I/O client.
A mixin class is also provided so that alternate data
handling can be implemented instead of the default in
SocketIO (e.g., by using one of the classes in the
ReadWrite module).
"""

from plib.stdlib.socketio import SocketIOBase, SocketData, SocketClientMixin
from plib.stdlib.ClientServer import ClientMixin

class ClientSocketMixin(SocketClientMixin, ClientMixin):
    """
    Mixin class to provide basic blocking socket client
    functionality. Call the client_communicate method to
    connect to a server and send data; override the
    process_data method to do something with the reply.
    """
    pass

class SocketClient(ClientSocketMixin, SocketData, SocketIOBase):
    """
    Basic blocking socket client class. Call the
    client_communicate method to connect to a server
    and send data; override the process_data method to
    do something with the reply.
    """
    pass
