#!/usr/bin/env python
"""
TEST_UTILS_CHATGEN.PY -- test script for sub-package UTILS of package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the chatgen module of
plib.utils.
"""

from plib.stdlib.AsyncServer import PersistentRequestHandler, ServerDispatcher
from plib.utils.chatgen import chat_replies

import stdlib_io_testlib

CHAT_ADDR = ('localhost', 11111)

class ChatHandler(PersistentRequestHandler):
    
    def process_data(self):
        self.start(self.read_data) # echo isn't the default for persistent!

class ChatClientTest(stdlib_io_testlib.IOChannelTest):
    
    handler_class = ChatHandler
    server_addr = CHAT_ADDR
    server_class = ServerDispatcher
    
    def test_chat_client(self):
        seq = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
        results = [reply for reply in chat_replies(CHAT_ADDR, seq)]
        self.assertEqual(results, seq)

class ChatClientTestCallback(stdlib_io_testlib.IOChannelTest):
    
    handler_class = ChatHandler
    server_addr = CHAT_ADDR
    server_class = ServerDispatcher
    
    def test_chat_callback(self):
        def callback():
            pass
        
        seq = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]
        results = [reply for reply in chat_replies(CHAT_ADDR, seq, callback)]
        self.assertEqual(results, seq)
