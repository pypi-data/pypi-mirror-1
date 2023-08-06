#!/usr/bin/env python
"""
Module SortMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the SortMixin class.
"""

class SortMixin(object):
    """
    Mixin class to allow insertion of objects into sequences
    in proper sorted order. Will work with any class that
    implements the insert method (note that calling insert
    with an index of len(self) should append the value to
    the end of the sequence, in accordance with the Python
    list semantics).
    
    The sort function used to compare values can be changed
    in one of two ways: either override _default_sortfunc
    (which will affect all sorted insertions where a sort
    function is not passed to the method as below), or pass
    a sort function to the insert_sorted method (which will
    only affect that particular insertion).
    """
    
    def _default_sortfunc(self, value1, value2):
        """
        Sorting function should return:
        
          negative integer if value1 < value2
          0 if value1 == value2
          positive integer if value1 > value2
        
        Default is to sort on str(value).
        """
        
        s1 = str(value1)
        s2 = str(value2)
        if s1 < s2:
            return -1
        elif s1 > s2:
            return 1
        else:
            return 0
    
    def _btree_index(self, value, sortfunc):
        # Return proper index at which to insert value based on sortfunc.
        start = 0
        end = len(self) - 1
        while start <= end:
            i = start + ((end - start) // 2)
            s = sortfunc(value, self[i])
            if s < 0:
                if i == 0:
                    # It's before all items in the list
                    return i
                end = i - 1
            elif s > 0:
                if i == (len(self) - 1):
                    # It's after all items in the list
                    return len(self)
                start = i + 1
            else:
                # Insert *after* equal value that's already in the list
                return i + 1
        # It's in between end and start, end < start so start is the higher index
        # and that's where it goes
        return start
    
    def insert_sorted(self, value, sortfunc=None):
        """
        Insert value in its proper place based on sorting function.
        """
        
        if sortfunc is None:
            sortfunc = self._default_sortfunc
        self.insert(self._btree_index(value, sortfunc), value)
