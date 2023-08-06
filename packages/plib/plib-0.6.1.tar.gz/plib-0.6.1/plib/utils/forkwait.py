#!/usr/bin/env python
"""
Module FORKWAIT -- Specialized Forking Function
Sub-Package UTILS of Package PLIB -- General Python Utilities
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the fork_wait function, which
forks a subprocess and then waits until the subprocess
has started before continuing.
"""

import os

server_ok = "1"

def fork_wait(start_fn, run_fn):
    rfd, wfd = os.pipe()
    server_pid = os.fork()
    if server_pid == 0:
        # server process
        try:
            os.close(rfd)
            try:
                start_fn()
                os.write(wfd, server_ok)
            finally:
                os.close(wfd)
            run_fn()
            os._exit(0)
        except Exception:
            os._exit(1)
    # client process
    os.close(wfd)
    try:
        ok = os.read(rfd, 1)
        if ok != server_ok:
            raise IOError, "fork_wait aborted!"
    finally:
        os.close(rfd)
    return server_pid
