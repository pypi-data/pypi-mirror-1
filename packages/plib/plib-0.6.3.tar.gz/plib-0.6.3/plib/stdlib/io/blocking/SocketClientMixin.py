#!/usr/bin/env python
"""
Module SocketClientMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SocketClientMixin class.
"""

from plib.stdlib.io.socket import BaseClient
from plib.stdlib.io.blocking import ClientMixin

class SocketClientMixin(BaseClient, ClientMixin):
    """
    Mixin class to provide basic blocking socket client
    functionality. Call the ``client_communicate`` method to
    connect to a server and send data; override the
    ``process_data`` method to do something with the reply.
    """
    
    pass
