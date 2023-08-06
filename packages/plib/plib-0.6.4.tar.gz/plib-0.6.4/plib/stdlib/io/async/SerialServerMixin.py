#!/usr/bin/env python
"""
Module SerialServerMixin
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SerialServerMixin class.
"""

from plib.stdlib.io.serial import BaseServer
from plib.stdlib.io.async import ServerMixin

class SerialServerMixin(BaseServer, ServerMixin):
    """
    Asynchronous server-side serial I/O mixin class. Call the
    ``serve_forever`` method to run the server. Note that the
    default is to remain open for an unlimited number of
    round-trip data exchanges; override the ``query_done`` method
    to determine when the server should close.
    """
    
    def serve_forever(self, callback=None):
        self.do_loop(callback) # simple alias for API compatibility
