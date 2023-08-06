#!/usr/bin/env python
"""
TEST_STDLIB_IO_NOPOLL.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the async I/O modules in
the PLIB.STDLIB sub-package, with the poll function disabled
(so that select must be used).
"""

import unittest

from plib.stdlib import async, AsyncServer, ReadWrite

import stdlib_io_testlib

async.use_poll = False # force use of select in all async loops

class NonBlockingSocketTestNoPoll(stdlib_io_testlib.ClientServerTest):
    
    client_class = AsyncServer.ClientCommunicator
    handler_class = AsyncServer.AsyncRequestHandler
    server_addr = ('localhost', 9999)
    server_class = AsyncServer.ServerDispatcher

class NonBlockingSocketTestLargeMessage1NoPoll(NonBlockingSocketTestNoPoll):
    
    server_addr = ('localhost', 8999)
    test_data = "a" * 6000

class NonBlockingSocketTestLargeMessage2NoPoll(NonBlockingSocketTestNoPoll):
    
    server_addr = ('localhost', 7999)
    test_data = "a" * 10000

class ReadWriteClientCommunicator(AsyncServer.ClientSocketMixin,
    ReadWrite.ReadWrite, AsyncServer.BaseSocket): pass

class ReadWriteRequestHandler(AsyncServer.ServerSocketMixin,
    ReadWrite.ReadWrite, AsyncServer.BaseRequestHandler): pass

class ReadWriteTestNoPoll(stdlib_io_testlib.ClientServerTest):
    
    client_class = ReadWriteClientCommunicator
    handler_class = ReadWriteRequestHandler
    server_addr = ('localhost', 9996)
    server_class = AsyncServer.ServerDispatcher

class ReadWriteTestLargeMessage1NoPoll(ReadWriteTestNoPoll):
    
    server_addr = ('localhost', 8996)
    test_data = "a" * 6000

class ReadWriteTestLargeMessage2NoPoll(ReadWriteTestNoPoll):
    
    server_addr = ('localhost', 7996)
    test_data = "a" * 10000

class TerminatorClientCommunicator(AsyncServer.ClientSocketMixin,
    ReadWrite.TerminatorReadWrite, AsyncServer.BaseSocket): pass

class TerminatorRequestHandler(AsyncServer.ServerSocketMixin,
    ReadWrite.TerminatorReadWrite, AsyncServer.BaseRequestHandler): pass

class TerminatorTestNoPoll(stdlib_io_testlib.ClientServerTest):
    
    client_class = TerminatorClientCommunicator
    handler_class = TerminatorRequestHandler
    server_addr = ('localhost', 9997)
    server_class = AsyncServer.ServerDispatcher

class TerminatorTestLargeMessage1NoPoll(TerminatorTestNoPoll):
    
    server_addr = ('localhost', 8997)
    test_data = "a" * 6000

class TerminatorTestLargeMessage2NoPoll(TerminatorTestNoPoll):
    
    server_addr = ('localhost', 7997)
    test_data = "a" * 10000

class ReadWritePersistentCommunicator(AsyncServer.PersistentSocketMixin,
    ReadWrite.ReadWrite, AsyncServer.BaseSocket): pass

class ReadWritePersistentRequestHandler(AsyncServer.PersistentMixin,
    ReadWrite.ReadWrite, AsyncServer.BaseRequestHandler): pass

class XPersistentTestNoPoll(stdlib_io_testlib.PersistentTest):
    
    client_class = ReadWritePersistentCommunicator
    handler_class = ReadWritePersistentRequestHandler
    server_addr = ('localhost', 9995)
    server_class = AsyncServer.ServerDispatcher
    
    client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
    server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]

class XPersistentTestLargeMessage1NoPoll(XPersistentTestNoPoll):
    
    client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
    server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    server_addr = ('localhost', 8995)

class XPersistentTestLargeMessage2NoPoll(XPersistentTestNoPoll):
    
    client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
    server_list = ["1" * 10000, "2" * 10000, "3" * 10000]
    server_addr = ('localhost', 7995)

class TerminatorPersistentCommunicator(AsyncServer.PersistentSocketMixin,
    ReadWrite.TerminatorReadWrite, AsyncServer.BaseSocket): pass

class TerminatorPersistentRequestHandler(AsyncServer.PersistentMixin,
    ReadWrite.TerminatorReadWrite, AsyncServer.BaseRequestHandler): pass

class YPersistentTestNoPoll(stdlib_io_testlib.PersistentTest):
    
    client_class = TerminatorPersistentCommunicator
    handler_class = TerminatorPersistentRequestHandler
    server_addr = ('localhost', 9994)
    server_class = AsyncServer.ServerDispatcher
    
    client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
    server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]

class YPersistentTestLargeMessage1NoPoll(XPersistentTestNoPoll):
    
    client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
    server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    server_addr = ('localhost', 8994)

class YPersistentTestLargeMessage2NoPoll(XPersistentTestNoPoll):
    
    client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
    server_list = ["1" * 10000, "2" * 10000, "3" * 10000]
    server_addr = ('localhost', 7994)

if __name__ == '__main__':
    unittest.main()
