#!/usr/bin/env python
"""
Module SigMixin
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the SigMixin class, which allows
forking servers to respond to SIGCHLD by reaping any
child processes that have completed.
"""

import signal
if not hasattr(signal, SIGCHLD):
    # Win32, at least, has no SIGCHLD; this makes this class
    # non-functional, but allows it to be imported and used
    # transparently
    signal.SIGCHLD = 0

class SigMixin(object):
    """
    Mixin class for forking servers to collect children when they
    exit instead of waiting for the next request. Note that since this
    class overrides ``collect_children``, it must be before the forking
    server class in the list of bases.
    
    Note that this implementation is compatible with the server
    classes in the Python standard library as well, so it can be used
    as a mixin with those classes if desired. In this case, the
    ``collect_on_signal`` flag should stay ``True``, so the SIGCHLD handler
    will reap children directly (and the ``child_waiting`` flag will not
    be used--it is mainly for mixing in with our ``SocketServer``).
    """
    
    child_waiting = False
    collect_on_signal = True
    
    def __init__(self):
        """
        Call this before calling the server ``__init__``.
        """
        
        signal.signal(signal.SIGCHLD, self.child_sig_handler)
        self.collecting = False
    
    def child_sig_handler(self, sig, frame):
        """
        Respond to SIGCHLD by collecting dead children.
        """
        
        self.child_waiting = True
        if self.collect_on_signal:
            self.collect_children()
        signal.signal(signal.SIGCHLD, self.child_sig_handler)
    
    def collect_children(self):
        """
        Wrap method to prevent re-entrant calls (the superclass
        ``collect_children`` will loop until all dead children are
        collected anyway, so ignoring overlapping calls is OK).
        """
        
        if not self.collecting:
            self.collecting = True
            super(SigMixin, self).collect_children()
            self.collecting = False
            self.child_waiting = False
