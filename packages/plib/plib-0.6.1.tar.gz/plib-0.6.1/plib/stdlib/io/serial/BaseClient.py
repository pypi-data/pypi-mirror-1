#!/usr/bin/env python
"""
Module BaseClient
Sub-Package STDLIB.IO.SERIAL of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the serial BaseClient class.
"""

class BaseClient(object):
    """
    Base class for serial I/O clients; implements the
    ``setup_client`` method (which is called from
    ``client_communicate``).
    """
    
    def setup_client(self, devid=None):
        """
        Open the serial device ID.
        """
        
        self.create_port(devid)
    
    def query_done(self):
        return False # serial clients should remain open until explicitly closed
