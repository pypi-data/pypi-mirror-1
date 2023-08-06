#!/usr/bin/env python
"""
Module PAsyncServer
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PAsyncServer class. This is an
asynchronous socket server that includes the general
signal and logging facilities of PServerBase.
"""

from plib.stdlib.AsyncServer import AsyncRequestHandler, ServerDispatcher

from PServerBase import PServerBase

class PAsyncServer(PServerBase, ServerDispatcher):
    """
    Generic async server class. Adds handling of the
    terminate_sig flag to do_loop.
    """
    
    bind_addr = ("localhost", 9999)
    handler_class = AsyncRequestHandler
    
    def __init__(self):
        PServerBase.__init__(self)
        ServerDispatcher.__init__(self, self.bind_addr, self.handler_class)
    
    def do_loop(self, callback=None):
        """
        Modify method to check the terminate_sig flag on each iteration
        of the async polling loop.
        """
        
        if callback is not None:
            c = callback
            def f():
                if self.terminate_sig is None:
                    return c()
                return False
        else:
            def f():
                if self.terminate_sig is None:
                    return None
                return False
        ServerDispatcher.do_loop(self, f)
