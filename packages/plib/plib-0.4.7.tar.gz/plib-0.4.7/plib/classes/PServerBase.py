#!/usr/bin/env python
"""
Module PServerBase
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PServerBase class.
"""

import sys
import os
import datetime

from signal import signal, SIGABRT, SIGCHLD, SIGHUP, SIGINT, SIGQUIT, SIGTERM

from PRequestHandler import PRequestHandler

class PServerBase(object):
    """
    Generic base server class, can be used with any type of server
    (sync, async, forking). Implements signal handling for controlled
    termination, and log file functionality. The intent is to trap any
    signal that might be used to indicate general 'program shutdown' as
    opposed to some specific error condition (i.e., any signal where it
    can be assumed that controlled shutdown of the Python interpreter
    is possible).
    """
    
    # We include SIGINT here because it appears to get masked when a script
    # is backgrounded, we want to unmask it just in case (we could go back
    # to the default Python handler that raises KeyboardInterrupt, but it's
    # easier just to trap it ourselves)
    sig_msgs = { SIGABRT: "aborted",
        SIGHUP: "hangup",
        SIGINT: "interrupt",
        SIGQUIT: "quit",
        SIGTERM: "terminated",
        None: "unknown shutdown" }
    ret_codes = { SIGHUP: 1, SIGQUIT: 2, SIGINT: 3, SIGABRT: 4, SIGTERM: 0, None: -1 }
    term_sigs = [SIGABRT, SIGHUP, SIGINT, SIGQUIT, SIGTERM]
    sig_methods = {}
    
    log_root = "~"
    log_namestr = "%(name)s.log"
    log_str = "%s %s, time %s\r\n"
    server_name = "server"
    
    bind_addr = ("localhost", 9999)
    handler_class = PRequestHandler
    
    redirect_files = True
    
    def __init__(self):
        # Decouple from parent environment -- we don't do the full daemonize 'double fork' since
        # we'll be run from a shell script that takes care of a lot of it; but we do want to
        # reset the working directory and redirect the standard file descriptors.
        if os.name == 'posix':
            os.chdir('/')
            self.dev_null = open(os.path.join("/dev", "null"), 'r')
            self.log_namestr = ".%(name)s/%(name)s.log"
        # TODO: what about other OS's like NT?
        
        log_filename = os.path.expanduser(os.path.join(self.log_root,
            self.log_namestr % {'name': self.server_name}))
        dir = os.path.dirname(log_filename)
        if dir and not os.path.isdir(dir):
            os.mkdir(dir)
        self.log_file = open(log_filename, 'a+', 0)
        self.log_name = self.server_name
        
        sys.stderr.flush()
        os.close(sys.stderr.fileno())
        os.dup2(self.log_file.fileno(), sys.stderr.fileno())
        if self.redirect_files:
            self.log_msg("redirecting standard file descriptors")
            sys.stdout.flush()
            os.close(sys.stdin.fileno())
            os.close(sys.stdout.fileno())
            os.dup2(self.dev_null.fileno(), sys.stdin.fileno())
            os.dup2(self.log_file.fileno(), sys.stdout.fileno())
        
        # Set up signal handlers
        self.terminate_sig = None
        for sig in self.term_sigs:
            signal(sig, self.term_sig_handler)
        
        # Log startup
        self.log_msg("started")
    
    def server_close(self):
        # Log shutdown
        self.log_msg(self.sig_msgs[self.terminate_sig])
        
        # Close the files we opened
        self.dev_null.close()
        self.log_file.close()
    
    def log_msg(self, msg):
        self.log_file.write(self.log_str % (self.log_name, msg, datetime.datetime.now()))
        self.log_file.flush()
    
    def ret_code(self):
        return self.ret_codes[self.terminate_sig]
    
    def term_sig_handler(self, sig, frame):
        """ Signal handler checks for dispatch method and calls it if present. Otherwise it
        just sets flag and returns; flag will be seen on next loop in serve_forever. """
        
        if sig in self.sig_methods:
            self.terminate_sig = getattr(self, self.sig_methods[sig])(sig, frame)
        else:
            self.terminate_sig = sig
