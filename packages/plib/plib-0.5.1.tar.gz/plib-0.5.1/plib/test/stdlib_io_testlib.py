#!/usr/bin/env python
"""
STDLIB_IO_TESTLIB.PY -- utility module for PLIB.STDLIB I/O tests
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains common code for the tests of the I/O
modules in PLIB.STDLIB.
"""

import os
import signal
import time
import unittest

from plib.stdlib.coll import fifo
from plib.utils.forkserver import fork_server

class IOChannelTest(unittest.TestCase):
    
    handler_class = None
    server_addr = None
    server_class = None
    
    def setUp(self):
        
        class IOServer(self.server_class):
            allow_reuse_address = True
        
        self.server_pid = fork_server(IOServer, self.server_addr, self.handler_class)
    
    def tearDown(self):
        os.kill(self.server_pid, signal.SIGTERM)
        os.waitpid(self.server_pid, 0)

# All the servers/request handlers default to "echo server" functionality,
# so we don't need to subclass any of those classes here.

class ClientServerTest(IOChannelTest):
    
    client_class = None
    test_data = "Python rocks!"
    
    def test_io(self):
        
        # The same subclassing works here for all the I/O client classes.
        class IOClient(self.client_class):
            result = ""
            def process_data(self):
                self.result = self.read_data
        
        client = IOClient()
        client.client_communicate(self.test_data, self.server_addr)
        self.assertEqual(client.result, self.test_data)

# Here we want to test interleaved full-duplex reads and writes, so
# we have the server/request handler send back different data, except
# for the sentinel at the end.

test_done = "All done!"
test_failed = "Oops, missed some data!"

class PersistentTestIO(object):
    
    queue_started = False
    received_list = None
    
    def writable(self):
        if self.data_queue and not self.queue_started:
            self.queue_started = True
            self.start(self.data_queue.next())
        return super(PersistentTestIO, self).writable()
    
    def process_data(self):
        if self.received_list is None:
            self.received_list = []
        self.received_list.append(self.read_data)

# The same mixin subclassing works here for any of the I/O request
# handler and client classes

def IOHandlerFactory(handler_class, queue_list, test_list):
    
    class IOHandler(PersistentTestIO, handler_class):
        data_queue = fifo(queue_list)
        def process_data(self):
            if self.read_data == test_done:
                if self.received_list == test_list:
                    self.start(test_done)
                else:
                    self.start(test_failed)
            else:
                PersistentTestIO.process_data(self)
    
    return IOHandler

def IOClientFactory(client_class, queue_list):
    
    class IOClient(PersistentTestIO, client_class):
        data_queue = fifo(queue_list + [test_done])
        def query_done(self):
            return (self.read_data in (test_done, test_failed))
    
    return IOClient

class PersistentTest(IOChannelTest):
    
    client_class = None
    client_list = None
    server_list = None
    
    def __init__(self, methodName='runTest'):
        self.handler_class = IOHandlerFactory(self.handler_class, self.server_list, self.client_list)
        self.client_class = IOClientFactory(self.client_class, self.client_list)
        IOChannelTest.__init__(self, methodName)
    
    def test_io(self):
        client = self.client_class()
        client.do_connect(self.server_addr)
        client.do_loop()
        self.assertEqual(client.received_list, self.server_list + [test_done])
