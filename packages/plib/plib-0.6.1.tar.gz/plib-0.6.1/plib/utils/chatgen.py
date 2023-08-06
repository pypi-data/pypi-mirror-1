#!/usr/bin/env python
"""
Module CHATGEN -- Generator wrappers for client/server I/O
Sub-Package UTILS of Package PLIB -- General Python Utilities
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``chat_replies`` class, which wraps an
asynchronous socket client so it looks like a generator. For
an example of usage, see the ``pyidserver.py`` example program.
"""

from plib.stdlib import coll
from plib.stdlib.io.async import loop, SocketClient

class chat_replies(SocketClient):
    """
    Generator that sends data items to a server one by one
    and yields the replies.
    """
    
    reply = ""
    
    def __init__(self, addr, items, callback=None):
        self.data_queue = coll.fifo(items)
        self.data_received = False
        SocketClient.__init__(self)
        
        if callback is not None:
            def f():
                return (callback() is not False) and (self.need_data() is not False)
            self.callback = f
        else:
            self.callback = self.need_data
        
        self.do_connect(addr)
    
    def start(self, data):
        self.data_received = False
        if data is not None:
            SocketClient.start(self, data)
    
    def need_data(self):
        return not self.data_received
    
    def process_data(self):
        self.reply = self.read_data
        self.data_received = True
    
    def query_done(self):
        return False # remain open until we're closed from the __iter__ method
    
    def __iter__(self):
        # Note that we can't wrap this in a try/finally to ensure self.close gets
        # called, because yields aren't allowed in try/finally in version 2.4 and
        # earlier; this is not fatal because handle_error calls self.close, and
        # any exception raised in async.loop calls handle_error, but it's inelegant
        while self.data_queue:
            self.clear_data()
            self.start(self.data_queue.next())
            loop(callback=self.callback)
            yield self.reply
        self.close()
