#!/usr/bin/env python
"""
Module BaseServer
Sub-Package STDLIB.IO.SERIAL of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the serial BaseServer class.
"""

class BaseServer(object):
    """
    Base class for serial I/O servers.
    """
    
    def query_done(self):
        return False # serial servers should remain open indefinitely
