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

import os
import serial # provided by pyserial package

from plib.stdlib.async import BaseData
from plib.stdlib.ReadWrite import TerminatorReadWrite

class SerialIOBase(object):
    """
    Base class for blocking serial I/O -- no frills, just
    reads and writes the serial device file. Note that we
    bypass the read and write methods of serial.Serial
    because they use async select calls, and those don't
    always seem to work well with device files. To use the
    async functionality, see the AsyncSerial module.
    """
    
    def __init__(self, devid=None):
        if devid:
            self.port = serial.Serial(devid)
        else:
            self.port = None
    
    def read(self, size=1):
        try:
            data = os.read(self.port.fd, size)
            return data
        except serial.SerialException:
            return ""
    
    def write(self, data):
        try:
            n = os.write(self.port.fd, data)
            return n
        except serial.SerialException:
            return 0
    
    def close(self):
        self.port.close()

class SerialIO(BaseData, SerialIOBase):
    """
    Serial I/O class that adds basic read/write handling; the
    only way this class has of detecting that a read is complete
    is when self.write_data becomes non-empty. Therefore, using
    this class usually requres that handle_read be overridden to
    check whether write_data should be filled in to signal that
    the read is complete.
    
    Note that the read/write handling can be overridden by using
    alternate handlers (e.g., the SerialIOWithTerminator class
    given below).
    """
    
    bufsize = 1
    
    def handle_read(self):
        data = self.read(self.bufsize)
        if data:
            self.read_data += data
    
    def read_complete(self):
        return not self.write_complete() # can't do much else without length detection
    
    def handle_write(self):
        written = self.write(self.write_data)
        self.write_data = self.write_data[written:]
    
    def write_complete(self):
        return not self.write_data

class SerialClientMixin(object):
    """
    Simple blocking serial I/O client: writes write_data, then
    reads back read_data, processes the read data, then clears
    data and waits for more.
    """
    
    def client_communicate(self, data):
        self.write_data = data
        while not self.write_complete():
            self.handle_write()
        while not self.read_complete():
            self.handle_read()
        self.process_data()
        self.clear_data()
    
    def process_data(self):
        """
        Derived classes should override to do something with the
        data read back.
        """
        pass

class SerialClient(SerialClientMixin, SerialIOBase): pass

class SerialServerMixin(object):
    """
    Simple blocking serial I/O server; reads data, processes it,
    writes back the result, then waits for more.
    """
    
    def server_communicate(self):
        while not self.read_complete():
            self.handle_read()
        self.process_data()
        while not self.write_complete():
            self.handle_write()
        self.clear_data()
    
    def process_data(self):
        """
        Derived classes should override to do more than echo
        data back to the client.
        """
        self.write_data = self.read_data
    
    def serve_forever(self):
        try:
            while True:
                self.server_communicate()
        finally:
            self.close()

class SerialServer(SerialServerMixin, SerialIO): pass

class SerialIOWithTerminator(TerminatorReadWrite, SerialIO): pass

class SerialClientWithTerminator(SerialClientMixin, SerialIOWithTerminator): pass

class SerialServerWithTerminator(SerialServerMixin, SerialIOWithTerminator): pass
