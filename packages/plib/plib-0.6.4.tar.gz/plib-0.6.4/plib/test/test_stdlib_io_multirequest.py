#!/usr/bin/env python
"""
TEST_STDLIB_IO_MULTIREQUEST.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests to ensure that the I/O servers in the
PLIB.STDLIB sub-package can handle multiple requests, both in sequence
and concurrent.
"""

import time
import unittest

from plib.stdlib.io import async, blocking

import stdlib_io_testlib

class SleepingHandler(blocking.BaseRequestHandler):
    
    def process_data(self):
        time.sleep(0.5)
        blocking.BaseRequestHandler.process_data(self)

class BlockingConcurrentRequestTest(stdlib_io_testlib.ConcurrentRequestTest):
    
    client_class = blocking.SocketClient
    handler_class = SleepingHandler
    server_addr = ('localhost', 14998)
    server_class = blocking.SocketServer

class BlockingConcurrentRequestTestWithGoCode(stdlib_io_testlib.ConcurrentRequestTest):
    
    client_class = blocking.SocketClient
    handler_class = blocking.BaseRequestHandler
    server_addr = ('localhost', 14988)
    server_class = blocking.SocketServer
    use_gocode = True

class BlockingMultiRequestTest(stdlib_io_testlib.MultiRequestTest):
    
    client_class = blocking.SocketClient
    handler_class = blocking.BaseRequestHandler
    server_addr = ('localhost', 13998)
    server_class = blocking.SocketServer

paused_handlers = {}

class PausingHandler(async.BaseRequestHandler):
    
    paused = ""
    
    def process_data(self):
        global paused_handlers
        self.paused = self.read_data
        paused_handlers[self._fileno] = (time.time(), self)
    
    def unpause(self):
        global paused_handlers
        del paused_handlers[self._fileno]
        self.start(self.paused)
        self.paused = ""

class PausingServer(async.SocketServer):
    
    poll_timeout = 0.5
    
    def check_paused_handlers(self):
        unpaused = []
        for key, value in paused_handlers.iteritems():
            t, handler = value
            if time.time() > (t + 0.5):
                unpaused.append(handler)
        for handler in unpaused:
            handler.unpause()
    
    def do_loop(self, callback=None):
        if callback is not None:
            def f():
                result = callback()
                if (result is not False) and paused_handlers:
                    self.check_paused_handlers()
                return result
        else:
            def f():
                if paused_handlers:
                    self.check_paused_handlers()
        async.SocketServer.do_loop(self, f)

class NonBlockingConcurrentRequestTest(stdlib_io_testlib.ConcurrentRequestTest):
    
    client_class = async.SocketClient
    handler_class = PausingHandler
    server_addr = ('localhost', 14999)
    server_class = PausingServer

class NonBlockingConcurrentRequestTestWithGoCode(stdlib_io_testlib.ConcurrentRequestTest):
    
    client_class = async.SocketClient
    handler_class = async.BaseRequestHandler
    server_addr = ('localhost', 14989)
    server_class = async.SocketServer
    use_gocode = True

class NonBlockingMultiRequestTest(stdlib_io_testlib.MultiRequestTest):
    
    client_class = async.SocketClient
    handler_class = async.BaseRequestHandler
    server_addr = ('localhost', 13999)
    server_class = async.SocketServer

if __name__ == '__main__':
    unittest.main()
