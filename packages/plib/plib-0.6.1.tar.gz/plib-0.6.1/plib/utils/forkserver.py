#!/usr/bin/env python
"""
Module FORKSERVER -- Server Forking Function
Sub-Package UTILS of Package PLIB -- General Python Utilities
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the fork_server function, which
forks a subprocess that starts a server of the given class,
and then waits until the server has started before continuing.
"""

from plib.utils.forkwait import fork_wait

class ServerProxy(object):
    
    def __init__(self, server_class, server_addr, handler_class):
        self.server_class = server_class
        self.server_addr = server_addr
        self.handler_class = handler_class
    
    def start_server(self):
        if self.handler_class is not None:
            self.server = self.server_class(self.server_addr, self.handler_class)
        elif self.server_addr is not None:
            self.server = self.server_class(self.server_addr)
        else:
            self.server = self.server_class()
    
    def run_server(self):
        self.server.serve_forever()

def fork_server(server_class, server_addr=None, handler_class=None):
    proxy = ServerProxy(server_class, server_addr, handler_class)
    return fork_wait(proxy.start_server, proxy.run_server)
