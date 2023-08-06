#!/usr/bin/env python
"""
Module SOCKETPAIR -- Socket Pair Forking Function
Sub-Package UTILS of Package PLIB -- General Python Utilities
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the fork_socketpair function, which
forks a subprocess that communicates with its parent via
a socket pair.
"""

import os
import socket

def fork_socketpair(fn):
    client_sock, daemon_sock = socket.socketpair()
    daemon_pid = os.fork()
    if daemon_pid == 0:
        # This is the child daemon process
        try:
            client_sock.close()
            fn(daemon_sock)
            os._exit(0)
        except Exception:
            daemon_sock.close()
            os._exit(1)
    # This is the parent process
    daemon_sock.close()
    return (client_sock, daemon_pid)
