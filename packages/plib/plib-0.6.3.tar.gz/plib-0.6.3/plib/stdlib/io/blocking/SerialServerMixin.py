#!/usr/bin/env python
"""
Module SerialServerMixin
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SerialServerMixin class.
"""

from plib.stdlib.io.serial import BaseServer
from plib.stdlib.io.blocking import ServerMixin

class SerialServerMixin(BaseServer, ServerMixin):
    """
    Blocking server-side serial I/O mixin class. Call the
    ``serve_forever`` method to run the server. Note that the
    default is to remain open for an unlimited number of
    round-trip data exchanges; override the ``query_done`` method
    to determine when the server should close.
    """
    
    def serve_forever(self):
        self.server_communicate()
