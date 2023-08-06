#!/usr/bin/env python
"""
Module BaseClient
Sub-Package STDLIB.IO.SOCKET of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the socket BaseClient class.
"""

from plib.stdlib.io.socket import ConnectMixin

class BaseClient(ConnectMixin):
    """
    Base class for socket clients, implements ``setup_client``
    method (which is called from ``client_communicate``).
    """
    
    def setup_client(self, addr=None):
        """
        Connect to server at addr.
        """
        
        self.do_connect(addr)
