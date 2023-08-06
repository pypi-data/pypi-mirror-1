#!/usr/bin/env python
"""
STDLIB_IO_TESTLIB.PY -- utility module for PLIB.STDLIB I/O tests
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common code for the tests of the I/O
modules in PLIB.STDLIB.
"""

import sys
import os
import signal
import socket
import unittest
from errno import EPIPE, ECONNRESET

from plib.stdlib.coll import fifo
from plib.utils.forkserver import fork_server
from plib.utils.socketpair import fork_socketpair

class IOChannelTest(unittest.TestCase):
    
    handler_class = None
    server_addr = None
    server_class = None
    
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        
        # Subclass the server class to ensure we can re-use addresses
        # for multiple tests
        class IOServer(self.server_class):
            allow_reuse_address = True
        IOServer.__name__ = self.server_class.__name__
        self.server_class = IOServer
    
    def setUp(self):
        self.server_pid = fork_server(self.server_class, self.server_addr, self.handler_class)
    
    def tearDown(self):
        os.kill(self.server_pid, signal.SIGTERM)
        os.waitpid(self.server_pid, 0)

# All the servers/request handlers default to "echo server" functionality,
# so we don't need to subclass any of those classes here.

class ClientServerTest(IOChannelTest):
    
    client_class = None
    test_data = "Python rocks!"
    
    def __init__(self, methodName='runTest'):
        IOChannelTest.__init__(self, methodName)
        
        # The same subclassing works here for all the I/O client classes.
        class IOClient(self.client_class):
            result = ""
            def process_data(self):
                self.result = self.read_data
        IOClient.__name__ = self.client_class.__name__
        self.client_class = IOClient
    
    def test_io(self):
        client = self.client_class()
        client.client_communicate(self.test_data, self.server_addr)
        self.assertEqual(client.result, self.test_data)

# This is to test proper behavior of the alternate read/write classes
# with small buffer sizes (meaning that the terminator or data size
# bytes may take multiple reads to arrive).

class SmallBufferTest(ClientServerTest):
    
    def __init__(self, methodName='runTest'):
        ClientServerTest.__init__(self, methodName)
        
        class SmallBufferClient(self.client_class):
            bufsize = 1
        SmallBufferClient.__name__ = self.client_class.__name__
        self.client_class = SmallBufferClient
        
        class SmallBufferHandler(self.handler_class):
            bufsize = 1
        SmallBufferHandler.__name__ = self.handler_class.__name__
        self.handler_class = SmallBufferHandler

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
    
    IOHandler.__name__ = handler_class.__name__
    return IOHandler

def IOClientFactory(client_class, queue_list):
    
    class IOClient(PersistentTestIO, client_class):
        data_queue = fifo(queue_list + [test_done])
        def query_done(self):
            return (self.read_data in (test_done, test_failed))
    
    IOClient.__name__ = client_class.__name__
    return IOClient

class PersistentTest(IOChannelTest):
    
    client_class = None
    client_list = None
    server_list = None
    
    def __init__(self, methodName='runTest'):
        IOChannelTest.__init__(self, methodName)
        
        # Subclass the handler and client classes to handle the data queues
        self.handler_class = IOHandlerFactory(self.handler_class, self.server_list, self.client_list)
        self.client_class = IOClientFactory(self.client_class, self.client_list)
    
    def test_io(self):
        client = self.client_class()
        client.do_connect(self.server_addr)
        client.do_loop()
        self.assertEqual(client.received_list, self.server_list + [test_done])

# Test the ability of the servers to handle multiple requests; first, we just
# run each client one at a time, so the requests come in serially (but the
# shutdown of one request handler may still overlap the start of the next)

def client_test(client_class, test_data, server_addr):
    client = client_class()
    try:
        client.client_communicate(test_data, server_addr)
        return client.result
    except Exception, e:
        return str(e)

class MultiRequestTest(ClientServerTest):
    
    request_num = 100
    
    def test_io(self):
        results = []
        for i in xrange(self.request_num):
            results.append(client_test(self.client_class, self.test_data, self.server_addr))
        self.assertEqual(results, [self.test_data] * self.request_num)

# Now test the handling of concurrent requests; we do this by forking all our
# clients so they can make requests simultaneously. We try this two ways, with
# and without a "go code" sent to each client by the master test object. With
# the go code, each client process makes its connection immediately, but doesn't
# send any data until the go code is received; this means the server is forced
# to maintain as many "waiting" requests as we have clients, until the clients
# start receiving go codes--but on the other hand, since each client gets woken
# up to send its go code sequentially, the requests will be handled in sequence
# (and closed in sequence, so the server will never see more than one closing
# child process at a time). Without the go code, each client tries to connect
# and do its round-trip data exchange as soon as it forks; here we impose a
# delay on the server end by forcing each request handler to wait for 0.5
# seconds before returning its reply, to try to keep as many concurrent
# connections pending as possible, so that requests will be handled in parallel
# (and consequently the server will be handling more than one closing child
# process at a time). Since we're not sure which case is harder for the server
# to handle, we test both ways.

go_code = "1"

def forking_client_test(client_class, test_data, server_addr, use_gocode):
    def f(sock):
        try:
            if use_gocode:
                client = client_class()
                client.do_connect(server_addr)
                try:
                    go = sock.recv(1)
                    if go == go_code:
                        try:
                            client.client_communicate(test_data)
                            sock.sendall(client.result)
                        except Exception, e:
                            sock.sendall(str(e))
                finally:
                    client.close()
            else:
                result = client_test(client_class, test_data, server_addr)
                sock.sendall(result)
        finally:
            sock.close()
    fsock, fpid = fork_socketpair(f)
    def r():
        result = ""
        try:
            try:
                if use_gocode:
                    fsock.sendall(go_code)
                result = fsock.recv(len(test_data))
            except socket.error, why:
                if why[0] not in (EPIPE, ECONNRESET):
                    raise
        finally:
            fsock.close()
        pid, exitcode = os.waitpid(fpid, 0)
        return (exitcode >> 8, result)
    return r

class ConcurrentRequestTest(ClientServerTest):
    
    if sys.platform == 'darwin':
        request_num = 15 # Mac OS X socket accept seems to be a lot slower than Linux...
    else:
        request_num = 100
    use_gocode = False
    
    def test_io(self):
        results = []
        for i in xrange(self.request_num):
            results.append(forking_client_test(self.client_class, self.test_data, self.server_addr, self.use_gocode))
        for i, result in enumerate(results):
            results[i] = result()
        self.assertEqual(results, [(0, self.test_data)] * self.request_num)
