#!/usr/bin/env python
"""
Module SerialIO -- Asynchronous Serial I/O Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains classes that provide serial I/O
functionality using the base provided in the async
module in this sub-package. Note that this module requires
the pyserial package, available on SourceForge.
"""

import serial # provided by pyserial package

from plib.stdlib.async import AsyncBase, BaseData, ClientMixin, ServerMixin
from plib.stdlib.ReadWrite import TerminatorReadWrite

class SerialDispatcher(AsyncBase):
    """
    Class to wrap a serial.Serial instance and provide
    asynchronous I/O using the AsyncBase mechanism.
    """
    
    def __init__(self, devid=None, map=None):
        AsyncBase.__init__(self, map)
        if devid:
            self.create_port(devid)
        else:
            self.port = None
    
    def create_port(self, devid):
        self.set_port(serial.Serial(devid))
    
    def set_port(self, port, map=None):
        self.port = port
        self.set_fileobj(port, map)
    
    def read(self, size=1):
        try:
            data = self.port.read(size)
            return data
        except serial.SerialException:
            return ""
    
    def write(self, data):
        try:
            self.port.write(data)
            return True
        except serial.SerialException:
            return False
    
    def close(self):
        AsyncBase.close(self)
        self.port.close()

class SerialIOBase(BaseData, SerialDispatcher):
    """
    Serial dispatcher class that adds basic read/write handling.
    Note that the read/write handling can be overridden by using
    alternate handlers (e.g., the SerialIOWithTerminator class
    given below).
    """
    
    bufsize = 8192
    
    def handle_read(self):
        data = self.read(self.bufsize)
        self.read_data += data
    
    def read_complete(self):
        return not self.write_complete() # can't do much else without length detection
    
    def handle_write(self):
        if self.write(self.write_data):
            self.write_data = ""
    
    def write_complete(self):
        return not self.write_data

class SerialClientMixin(ClientMixin): pass # TODO: do we need anything here?

class SerialClient(SerialClientMixin, SerialIOBase): pass

class SerialServerMixin(ServerMixin):
    
    def query_done(self):
        """
        Default for serial servers is to remain open indefinitely.
        """
        return False

class SerialServer(SerialServerMixin, SerialIOBase): pass

class SerialIOWithTerminator(TerminatorReadWrite, SerialIOBase): pass

class SerialClientWithTerminator(SerialClientMixin, SerialIOWithTerminator): pass

class SerialServerWithTerminator(SerialServerMixin, SerialIOWithTerminator): pass
