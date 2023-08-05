#!/usr/bin/env python
"""
Module abstractlist
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractlist class.
"""

import sys

from plib.stdlib import abstractsequence

class abstractlist(abstractsequence):
    """
    Abstract base class to match list functionality but minimize the
    number of methods that must be implemented in subclasses.
    
    The only methods which *must* be implemented are __len__, __getitem__,
    __setitem__, and __delitem__. Also, it will almost always be necessary
    to override __init__ to initialize the underlying data structure *before*
    calling up to this class's __init__ (which will populate the data structure
    if a sequence is passed to the constructor), and __len__ to more
    efficiently calculate the length of the list. It may also be advantageous
    to reimplement __iter__ if a more efficient method of iterating through
    the underlying data structure exists (this will depend on how expensive
    the __getitem__ call is vs. the reimplemented iterator), and __contains__
    if a more efficient membership test exists. Finally, note that sort is
    not implemented in this class, since duplicating the built-in sort algorithm
    is highly problematic without knowledge of the underlying data structure;
    therefore sort functionality must be implemented as well if desired.
    
    The key, of course, is that, unlike the situation when one wants to
    subclass the built-in list class to overlay a different data structure,
    here you do *not* have to override all the other mutable sequence
    methods, append, insert, etc., because in this abstract class they all
    use the above methods to do their work. Another way of putting this
    point would be to raise the question whether the built-in Python
    list implementation, which does not have this feature, is a case of
    premature optimization. :)
    """
    
    def __init__(self, sequence=None):
        """
        Subclasses should initialize the underlying data structure *before*
        calling up to this method.
        """
        if sequence is not None:
            self.extend(sequence)
    
    # __len__, __getitem__, and __setitem__ are inherited from abstractsequence
    
    def __delitem__(self, index):
        """
        Delete item by index. Negative indexes are relative to end of list.
        Raise IndexError if index is out of range.
        """
        raise NotImplementedError
    
    if sys.version_info < (2, 0):
        # Include these only in old versions that require them
        def __getslice__(self, i, j):
            return self.__getitem__(slice(max(0, i), max(0, j)))
        def __setslice__(self, i, j, seq):
            self.__setitem__(slice(max(0, i), max(0, j)), seq)
        def __delslice__(self, i, j):
            self.__delitem__(slice(max(0, i), max(0, j)))
    
    # __iter__, __contains__, and the comparison operators are inherited from
    # abstractsequence
    
    def __add__(self, other):
        if hasattr(other, '__iter__'):
            result = self.__class__(self)
            result.extend(other)
            return result
        else:
            raise TypeError, "Cannot add a non-iterable to a sequence."
    
    # __radd__ is inherited from abstractsequence
    
    def __iadd__(self, other):
        if hasattr(other, '__iter__'):
            self.extend(other)
            return self
        else:
            raise TypeError, "Cannot add a non-iterable to a sequence."
    
    def __mul__(self, other):
        if isinstance(other, int):
            result = self.__class__()
            if other < 0:
                raise ValueError, "Cannot multiply sequence by a negative number."
            elif other > 0:
                seq = self[:]
                for i in range(other):
                    result.extend(seq) # need the slice copy since we'll mutate self
            return result
        else:
            raise TypeError, "Can only multiply a sequence by an integer."
    
    __rmul__ = __mul__
    
    def __imul__(self, other):
        if isinstance(other, int):
            if other < 0:
                raise ValueError, "Cannot multiply sequence by a negative number."
            elif other == 0:
                self.clear()
            else:
                seq = self[:]
                for i in range(other - 1):
                    self.extend(seq)
            return self
        else:
            raise TypeError, "Can only multiply a sequence by an integer."
    
    # index and count are inherited from abstractsequence
    
    def append(self, value):
        self.extend((value,))
    
    def extend(self, sequence):
        if hasattr(sequence, '__iter__'):
            self.__setitem__(slice(self.__len__(), self.__len__()), sequence)
        else:
            raise TypeError, "Can only extend by an iterable."
    
    def insert(self, index, value):
        self.__setitem__(slice(index, index), (value,))
    
    def remove(self, value):
        self.__delitem__(self.index(value))
    
    def pop(self, index=-1):
        result = self.__getitem__(index)
        self.__delitem__(index)
        return result
    
    def reverse(self):
        last = self.__len__() - 1
        for index in range((last + 1)/2):
            dual = last - index
            item = self.__getitem__(index)
            self.__setitem__(index, self.__getitem__(dual))
            self.__setitem__(dual, item)
    
    def sort(self, cmp=None, key=str.lower, reverse=False):
        """ Sort the list items in place. """
        raise NotImplementedError
    
    # We add this one method here for convenience although normally only
    # mappings have it, not sequences
    
    def clear(self):
        """ Remove all elements from the list. """
        while self.__len__() > 0:
            self.pop()
