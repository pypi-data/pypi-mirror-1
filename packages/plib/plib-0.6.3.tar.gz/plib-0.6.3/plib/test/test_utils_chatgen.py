#!/usr/bin/env python
"""
TEST_UTILS_CHATGEN.PY -- test script for sub-package UTILS of package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the chatgen module of
plib.utils.
"""

from plib.stdlib.io.async import PersistentRequestHandler, SocketServer
from plib.utils.chatgen import chat_replies

import stdlib_io_testlib

class ChatHandler(PersistentRequestHandler):
    
    def process_data(self):
        self.start(self.read_data) # echo isn't the default for persistent!

class ChatClientTest(stdlib_io_testlib.IOChannelTest):
    
    handler_class = ChatHandler
    server_addr = ('localhost', 11111)
    server_class = SocketServer
    
    def test_chat_client(self):
        seq = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
        results = [reply for reply in chat_replies(self.server_addr, seq)]
        self.assertEqual(results, seq)

class ChatClientTestCallback(stdlib_io_testlib.IOChannelTest):
    
    handler_class = ChatHandler
    server_addr = ('localhost', 11112)
    server_class = SocketServer
    
    def test_chat_callback(self):
        def callback():
            pass
        
        seq = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]
        results = [reply for reply in chat_replies(self.server_addr, seq, callback)]
        self.assertEqual(results, seq)

start_msg = "Started!"

class ChatHandlerNone(ChatHandler):
    
    def __init__(self, request, client_address, server):
        ChatHandler.__init__(self, request, client_address, server)
        self.start(start_msg)

class ChatClientTestWithNone(stdlib_io_testlib.IOChannelTest):
    
    handler_class = ChatHandlerNone
    server_addr = ('localhost', 11113)
    server_class = SocketServer
    
    def test_chat_client(self):
        seq = [None, "Python rocks!", "Try it today!", "You'll be glad you did!"]
        results = [reply for reply in chat_replies(self.server_addr, seq)]
        self.assertEqual(results, [start_msg] + seq[1:])

if __name__ == '__main__':
    unittest.main()
