#!/usr/bin/env python
"""
Module CHATGEN -- Generator wrappers for client/server I/O
Sub-Package UTILS of Package PLIB -- General Python Utilities
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the chat_replies class, which wraps an
asynchronous socket client so it looks like a generator. For
an example of usage, see the pyidserver.py example program.
"""

from plib.stdlib import async, coll, AsyncServer

class chat_replies(AsyncServer.ClientCommunicator):
    """
    Generator that sends data items to a server one by one
    and yields the replies.
    """
    
    def __init__(self, addr, items, callback=None):
        self.data_queue = coll.fifo(items)
        self.data_received = False
        AsyncServer.ClientCommunicator.__init__(self)
        
        if callback is not None:
            def f():
                return (callback() is not False) and (self.need_data() is not False)
            self.callback = f
        else:
            self.callback = self.need_data
        
        self.do_connect(addr)
    
    def start(self, data):
        self.data_received = False
        AsyncServer.ClientCommunicator.start(self, data)
    
    def need_data(self):
        return not self.data_received
    
    def process_data(self):
        self.data_received = True
    
    def query_done(self):
        return False # remain open until we're closed from the __iter__() method
    
    def __iter__(self):
        while self.data_queue:
            self.clear_data()
            self.start(str(self.data_queue.next()))
            async.loop(callback=self.callback)
            yield self.read_data
        self.close()
