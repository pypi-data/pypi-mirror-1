#!/usr/bin/env python
"""
TEST_STDLIB_IO_NOPOLL.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the async I/O modules in
the PLIB.STDLIB sub-package, with the poll function disabled
(so that select must be used).
"""

import unittest

from plib.stdlib.io import async, blocking, data

import stdlib_io_testlib

async.use_poll = False # force use of select in all async loops

class NonBlockingSocketTestNoPoll(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClient
    handler_class = async.BaseRequestHandler
    server_addr = ('localhost', 29999)
    server_class = async.SocketServer

class NonBlockingSocketTestBufsizeNoPoll(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClientWithShutdown
    handler_class = async.BaseRequestHandlerWithShutdown
    server_addr = ('localhost', 49999)
    server_class = async.SocketServer
    test_data = "x" * async.SocketClientWithShutdown.bufsize

class NonBlockingSocketTestLargeMessage1NoPoll(NonBlockingSocketTestNoPoll):
    
    server_addr = ('localhost', 28999)
    test_data = "a" * 6000

class NonBlockingSocketTestLargeMessage2NoPoll(NonBlockingSocketTestNoPoll):
    
    server_addr = ('localhost', 27999)
    test_data = "a" * 10000

class ReadWriteTestNoPoll(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClientWithReadWrite
    handler_class = async.BaseRequestHandlerWithReadWrite
    server_addr = ('localhost', 29996)
    server_class = async.SocketServer

class ReadWriteTestBufsizeNoPoll(ReadWriteTestNoPoll):
    
    server_addr = ('localhost', 49996)
    # total data including read/write encoding should be exactly one buffer
    test_data = "x" * (async.SocketClientWithReadWrite.bufsize
        - len(str(async.SocketClientWithReadWrite.bufsize))
        - len(async.SocketClientWithReadWrite.bufsep))

class ReadWriteTestLargeMessage1NoPoll(ReadWriteTestNoPoll):
    
    server_addr = ('localhost', 28996)
    test_data = "a" * 6000

class ReadWriteTestLargeMessage2NoPoll(ReadWriteTestNoPoll):
    
    server_addr = ('localhost', 27996)
    test_data = "a" * 10000

class ReadWriteTestSmallBufferNoPoll(stdlib_io_testlib.SmallBufferTest):
    
    client_class = async.SocketClientWithReadWrite
    handler_class = async.BaseRequestHandlerWithReadWrite
    server_addr = ('localhost', 26996)
    server_class = async.SocketServer

class TerminatorTestNoPoll(stdlib_io_testlib.ClientServerTest):
    
    client_class = async.SocketClientWithTerminator
    handler_class = async.BaseRequestHandlerWithTerminator
    server_addr = ('localhost', 29997)
    server_class = async.SocketServer

class TerminatorTestBufsizeNoPoll(TerminatorTestNoPoll):
    
    server_addr = ('localhost', 49997)
    # total data including terminator should be exactly one buffer
    test_data = "x" * (async.SocketClientWithTerminator.bufsize
        - len(async.SocketClientWithTerminator.terminator))

class TerminatorTestLargeMessage1NoPoll(TerminatorTestNoPoll):
    
    server_addr = ('localhost', 28997)
    test_data = "a" * 6000

class TerminatorTestLargeMessage2NoPoll(TerminatorTestNoPoll):
    
    server_addr = ('localhost', 27997)
    test_data = "a" * 10000

class TerminatorTestSmallBufferNoPoll(stdlib_io_testlib.SmallBufferTest):
    
    client_class = async.SocketClientWithTerminator
    handler_class = async.BaseRequestHandlerWithTerminator
    server_addr = ('localhost', 26997)
    server_class = async.SocketServer

class XPersistentTestNoPoll(stdlib_io_testlib.PersistentTest):
    
    client_class = async.PersistentSocketWithReadWrite
    handler_class = async.PersistentRequestHandlerWithReadWrite
    server_addr = ('localhost', 29995)
    server_class = async.SocketServer
    
    client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
    server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]

class XPersistentTestLargeMessage1NoPoll(XPersistentTestNoPoll):
    
    client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
    server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    server_addr = ('localhost', 28995)

class XPersistentTestLargeMessage2NoPoll(XPersistentTestNoPoll):
    
    client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
    server_list = ["1" * 10000, "2" * 10000, "3" * 10000]
    server_addr = ('localhost', 27995)

class YPersistentTestNoPoll(stdlib_io_testlib.PersistentTest):
    
    client_class = async.PersistentSocketWithTerminator
    handler_class = async.PersistentRequestHandlerWithTerminator
    server_addr = ('localhost', 29994)
    server_class = async.SocketServer
    
    client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
    server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]

class YPersistentTestLargeMessage1NoPoll(YPersistentTestNoPoll):
    
    client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
    server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    server_addr = ('localhost', 28994)

class YPersistentTestLargeMessage2NoPoll(YPersistentTestNoPoll):
    
    client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
    server_list = ["1" * 10000, "2" * 10000, "3" * 10000]
    server_addr = ('localhost', 27994)

if __name__ == '__main__':
    unittest.main()
