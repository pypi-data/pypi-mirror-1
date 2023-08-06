#!/usr/bin/env python
"""
TEST_UTILS_FORK.PY -- test script for plib.utils forking functions
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the forking functions in
the plib.utils sub-package.
"""

import os
import socket
import unittest
from errno import EPIPE, ECONNRESET

from plib.utils.forkwait import fork_wait
from plib.utils.socketpair import fork_socketpair

def dummy_fn():
    pass

def bad_fn():
    raise Exception

def forkwait_test(f1, f2):
    pid = fork_wait(f1, f2)
    pid, exitcode = os.waitpid(pid, 0)
    return exitcode >> 8

test_byte = "1"

def socket_fn(sock):
    try:
        s = sock.recv(1)
        sock.sendall(s)
    finally:
        sock.close()

def bad_socket_fn(sock):
    raise Exception

def socketpair_test(f, use_except=False):
    sock, pid = fork_socketpair(f)
    try:
        try:
            sock.sendall(test_byte)
            result = sock.recv(1)
        except socket.error, why:
            # Catch expected error if child process throws exception
            # and closes its socket; this is a more precise test than
            # just using assertRaises(socket.error, ...) in the test
            # case (since that would catch all socket errors, not just
            # the ones we want). We'll test whether the child branch
            # of fork_socketpair exited correctly when we test its
            # exit code (should be 1 on any exception). Note that the
            # OS will not always return the same error code: it's
            # something of a crapshoot whether it's broken pipe or
            # connection reset by peer.
            if (not use_except) or (why[0] not in (EPIPE, ECONNRESET)):
                raise
            result = ""
    finally:
        sock.close()
    pid, exitcode = os.waitpid(pid, 0)
    return (exitcode >> 8, result)

class ForkWaitTest(unittest.TestCase):
    
    def test_forkwait(self):
        self.assertEqual(forkwait_test(dummy_fn, dummy_fn), 0)
        self.assertEqual(forkwait_test(dummy_fn, bad_fn), 1)
        self.assertEqual(forkwait_test(dummy_fn, None), 1)
        self.assertRaises(IOError, forkwait_test, bad_fn, None)
        self.assertRaises(IOError, forkwait_test, None, None)

class SocketPairTest(unittest.TestCase):
    
    def test_socketpair(self):
        self.assertEqual(socketpair_test(socket_fn), (0, test_byte))
        self.assertEqual(socketpair_test(bad_socket_fn, True), (1, ""))
        self.assertEqual(socketpair_test(None, True), (1, ""))

if __name__ == '__main__':
    unittest.main()
