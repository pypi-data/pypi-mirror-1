#!/usr/bin/env python
"""
Module PAsyncServer
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PAsyncServer class.
"""

from plib.stdlib.AsyncServer import ServerDispatcher

from PServerBase import PServerBase

class PAsyncServer(PServerBase, ServerDispatcher):
    """
    Generic async server class.
    """
    
    def __init__(self):
        PServerBase.__init__(self)
        ServerDispatcher.__init__(self, self.bind_addr, self.handler_class)
    
    def server_close(self):
        ServerDispatcher.server_close(self)
        PServerBase.server_close(self)
    
    def do_loop(self, callback=None):
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
