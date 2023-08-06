#!/usr/bin/env python
"""
Module RequestBase
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous RequestBase class.
"""

from plib.stdlib.io.socket import BaseRequest
from plib.stdlib.io.async import SocketBase

class RequestBase(BaseRequest, SocketBase):
    """
    Asynchronous socket I/O set up to serve as a request handler.
    """
    
    def __init__(self, request, client_addr, server):
        BaseRequest.__init__(self, request, client_addr, server)
        SocketBase.__init__(self, request)
