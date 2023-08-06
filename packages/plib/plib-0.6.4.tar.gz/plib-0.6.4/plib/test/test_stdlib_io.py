#!/usr/bin/env python
"""
TEST_STDLIB_IO.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the I/O modules in the
PLIB.STDLIB sub-package.
"""

import unittest

from plib.stdlib.io import async, blocking, data

import stdlib_io_testlib

async.use_poll = True # ensure that we use poll if available

class BlockingSocketTest(stdlib_io_testlib.ClientServerTest):
    
    client_class = blocking.SocketClient
    handler_class = blocking.BaseRequestHandler
    server_addr = ('localhost', 9998)
    server_class = blocking.SocketServer

class BlockingSocketTestBufsize(stdlib_io_testlib.ClientServerTest):
    
    client_class = blocking.SocketClientWithShutdown
    handler_class = blocking.BaseRequestHandlerWithShutdown
    server_addr = ('localhost', 59998)
    server_class = blocking.SocketServer
    test_data = "x" * blocking.SocketClientWithShutdown.bufsize

class BlockingSocketTestLargeMessage1(BlockingSocketTest):
    
    server_addr = ('localhost', 8998)
    test_data = "a" * 6000

class BlockingSocketTestLargeMessage2(BlockingSocketTest):
    
    server_addr = ('localhost', 7998)
    test_data = "a" * 10000

class BlockingSocketTestReadWrite(stdlib_io_testlib.ClientServerTest):
    
    client_class = blocking.SocketClientWithReadWrite
    handler_class = blocking.BaseRequestHandlerWithReadWrite
    server_addr = ('localhost', 9098)
    server_class = blocking.SocketServer

class BlockingSocketTestTerminator(stdlib_io_testlib.ClientServerTest):
    
    client_class = blocking.SocketClientWithTerminator
    handler_class = blocking.BaseRequestHandlerWithTerminator
    server_addr = ('localhost', 9198)
    server_class = blocking.SocketServer

class NonBlockingSocketTest(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClient
    handler_class = async.BaseRequestHandler
    server_addr = ('localhost', 9999)
    server_class = async.SocketServer

class NonBlockingSocketTestBufsize(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClientWithShutdown
    handler_class = async.BaseRequestHandlerWithShutdown
    server_addr = ('localhost', 59999)
    server_class = async.SocketServer
    test_data = "x" * async.SocketClientWithShutdown.bufsize

class NonBlockingSocketTestLargeMessage1(NonBlockingSocketTest):
    
    server_addr = ('localhost', 8999)
    test_data = "a" * 6000

class NonBlockingSocketTestLargeMessage2(NonBlockingSocketTest):
    
    server_addr = ('localhost', 7999)
    test_data = "a" * 10000

class ReadWriteTest(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClientWithReadWrite
    handler_class = async.BaseRequestHandlerWithReadWrite
    server_addr = ('localhost', 9996)
    server_class = async.SocketServer

class ReadWriteTestBufsize(ReadWriteTest):
    
    server_addr = ('localhost', 59996)
    # total data including read/write encoding should be exactly one buffer
    test_data = "x" * (async.SocketClientWithReadWrite.bufsize
        - len(str(async.SocketClientWithReadWrite.bufsize))
        - len(async.SocketClientWithReadWrite.bufsep))

class ReadWriteTestLargeMessage1(ReadWriteTest):
    
    server_addr = ('localhost', 8996)
    test_data = "a" * 6000

class ReadWriteTestLargeMessage2(ReadWriteTest):
    
    server_addr = ('localhost', 7996)
    test_data = "a" * 10000

class ReadWriteTestSmallBuffer(stdlib_io_testlib.SmallBufferTest):
    
    client_class = async.SocketClientWithReadWrite
    handler_class = async.BaseRequestHandlerWithReadWrite
    server_addr = ('localhost', 6996)
    server_class = async.SocketServer

class TerminatorTest(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClientWithTerminator
    handler_class = async.BaseRequestHandlerWithTerminator
    server_addr = ('localhost', 9997)
    server_class = async.SocketServer

class TerminatorTestBufsize(TerminatorTest):
    
    server_addr = ('localhost', 59997)
    # total data including terminator should be exactly one buffer
    test_data = "x" * (async.SocketClientWithTerminator.bufsize
        - len(async.SocketClientWithTerminator.terminator))

class TerminatorTestLargeMessage1(TerminatorTest):
    
    server_addr = ('localhost', 8997)
    test_data = "a" * 6000

class TerminatorTestLargeMessage2(TerminatorTest):
    
    server_addr = ('localhost', 7997)
    test_data = "a" * 10000

class TerminatorTestSmallBuffer(stdlib_io_testlib.SmallBufferTest):
    
    client_class = async.SocketClientWithTerminator
    handler_class = async.BaseRequestHandlerWithTerminator
    server_addr = ('localhost', 6997)
    server_class = async.SocketServer

class XPersistentTest(stdlib_io_testlib.PersistentTest):
    
    client_class = async.PersistentSocketWithReadWrite
    handler_class = async.PersistentRequestHandlerWithReadWrite
    server_addr = ('localhost', 9995)
    server_class = async.SocketServer
    
    client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
    server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]

class XPersistentTestLargeMessage1(XPersistentTest):
    
    client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
    server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    server_addr = ('localhost', 8995)

class XPersistentTestLargeMessage2(XPersistentTest):
    
    client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
    server_list = ["1" * 10000, "2" * 10000, "3" * 10000]
    server_addr = ('localhost', 7995)

class YPersistentTest(stdlib_io_testlib.PersistentTest):
    
    client_class = async.PersistentSocketWithTerminator
    handler_class = async.PersistentRequestHandlerWithTerminator
    server_addr = ('localhost', 9994)
    server_class = async.SocketServer
    
    client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
    server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]

class YPersistentTestLargeMessage1(YPersistentTest):
    
    client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
    server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    server_addr = ('localhost', 8994)

class YPersistentTestLargeMessage2(YPersistentTest):
    
    client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
    server_list = ["1" * 10000, "2" * 10000, "3" * 10000]
    server_addr = ('localhost', 7994)

if __name__ == '__main__':
    unittest.main()
