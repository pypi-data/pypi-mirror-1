#!/usr/bin/env python
"""
Module SocketBase
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SocketBase class.
"""

from plib.stdlib.io.socket import SocketData
from plib.stdlib.io.async import SocketDispatcher

class SocketBase(SocketData, SocketDispatcher):
    """
    Socket async I/O class with data handling and defaults
    for events that don't need handlers.
    """
    
    def handle_connect(self):
        pass # don't need any warning here
    
    def handle_expt(self):
        pass # ignore any out of band data
    
    def handle_close(self):
        pass # don't need any warning here
