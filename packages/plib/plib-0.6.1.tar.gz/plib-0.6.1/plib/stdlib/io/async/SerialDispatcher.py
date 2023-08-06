#!/usr/bin/env python
"""
Module SerialDispatcher -- Asynchronous Serial I/O
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a basic asynchronous serial I/O
dispatcher.
"""

from plib.stdlib.io.serial import SerialIOBase

from _async import AsyncBase

class SerialDispatcher(SerialIOBase, AsyncBase):
    """
    Class to wrap a serial device file and provide
    asynchronous I/O using the ``AsyncBase`` mechanism.
    """
    
    closed = False
    
    def __init__(self, devid=None, map=None):
        AsyncBase.__init__(self, map)
        SerialIOBase.__init__(self, devid)
    
    def set_port(self, port):
        SerialIOBase.set_port(self, port)
        self.set_fileobj(port, self._map)
    
    def close(self):
        AsyncBase.close(self)
        
        # Check closed flag so we only close the port
        # once, even if this method is called multiple
        # times from different trigger events
        if not self.closed:
            self.port.close()
            self.closed = True
