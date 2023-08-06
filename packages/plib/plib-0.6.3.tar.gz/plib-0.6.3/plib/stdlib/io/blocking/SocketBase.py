#!/usr/bin/env python
"""
Module SocketBase
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SocketBase class.
"""

from plib.stdlib.io.socket import SocketData, SocketIOBase

class SocketBase(SocketData, SocketIOBase):
    """
    Base blocking socket I/O class with data handling.
    """
    
    pass

