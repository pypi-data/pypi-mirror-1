#!/usr/bin/env python
"""
Module COLL -- Convenience Collection Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains some additional collection classes
with method names redefined for greater convenience. The
key desire here is to have the method names 'append' and
'next' refer to the methods that you *want* to call for
each collection to add and retrieve an item from the
"right" place (i.e., the "next" item for the given
collection). Thus:

fifo -- a deque; 'append' adds to the end of the queue,
'next' retrieves from the start (i.e., 'popleft').

stack -- a list; 'append' adds to the end of the list,
'next' retrieves from the end as well (i.e., 'pop').
"""

import collections

class fifo(collections.deque):
    """
    A first-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.next = self.popleft
        collections.deque.__init__(self, *args, **kwargs)

class stack(list):
    """
    A last-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.next = self.pop
        list.__init__(self, *args, **kwargs)
