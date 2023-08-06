#!/usr/bin/env python
"""
TEST_STDLIB_IO_MULTIREQUEST.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests to ensure that the I/O servers in the
PLIB.STDLIB sub-package can handle multiple requests, both in sequence
and concurrent.
"""

import unittest

from plib.stdlib import AsyncServer, SigSocketServer, SocketClient

import stdlib_io_testlib

class BlockingMultiRequestTest(stdlib_io_testlib.MultiRequestTest):
    
    client_class = SocketClient.SocketClient
    handler_class = SigSocketServer.BaseRequestHandler
    server_addr = ('localhost', 13998)
    server_class = SigSocketServer.SigForkingTCPServer

class NonBlockingMultiRequestTest(stdlib_io_testlib.MultiRequestTest):
    
    client_class = AsyncServer.ClientCommunicator
    handler_class = AsyncServer.AsyncRequestHandler
    server_addr = ('localhost', 13999)
    server_class = AsyncServer.ServerDispatcher

class BlockingConcurrentRequestTest(stdlib_io_testlib.ConcurrentRequestTest):
    
    client_class = SocketClient.SocketClient
    handler_class = SigSocketServer.BaseRequestHandler
    server_addr = ('localhost', 14998)
    server_class = SigSocketServer.SigForkingTCPServer

class NonBlockingConcurrentRequestTest(stdlib_io_testlib.ConcurrentRequestTest):
    
    client_class = AsyncServer.ClientCommunicator
    handler_class = AsyncServer.AsyncRequestHandler
    server_addr = ('localhost', 14999)
    server_class = AsyncServer.ServerDispatcher

if __name__ == '__main__':
    unittest.main()
