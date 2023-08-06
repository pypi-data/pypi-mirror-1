#!/usr/bin/env python
"""
Module abstractsequence
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractsequence class.
"""

from plib.stdlib import inrange, abstractcontainer

class abstractsequence(abstractcontainer):
    """
    An abstract sequence whose length cannot be changed.
    
    This class can be used to provide a sequence-like view of data
    structures whose length should not be mutable, but whose elements
    can be re-bound to new objects (unlike a tuple, whose elements
    can't be changed, although if the element objects themselves are
    mutable, they can be mutated in-place).
    
    Note: this class does not implement any mechanism to initialize
    the sequence from another one (i.e., to be able to call the
    constructor with another sequence as an argument, as the tuple
    constructor can be called). Subclasses that desire such a
    mechanism must implement it with an overridden constructor, and
    must ensure that the mechanism is compatible with the __len__
    and __setitem__ methods (so that those methods will not return
    an index out of range error during the initialization process).
    """
    
    # __len__, __getitem__, __iter__, and __contains__
    # are inherited from abstractcontainer
    
    def __setitem__(self, index, value):
        """
        Set item by index. Negative indexes are relative to end of sequence.
        Raise IndexError if index is out of range.
        """
        raise NotImplementedError
    
    #def __repr__(self):
    #    return "".join(("[", ", ".join([repr(item) for item in self.__iter__()]), "]"))
    #
    #__str__ = __repr__
    
    def __ne__(self, other):
        if len(other) != self.__len__():
            return True
        for i, j in zip(self, other):
            if i != j:
                return True
        return False
    
    def __eq__(self, other):
        return not self.__ne__(other)
    
    def __lt__(self, other):
        return (self.__len__() < len(other))
    
    def __gt__(self, other):
        return (self.__len__() > len(other))
    
    def __le__(self, other):
        return (self.__len__() <= len(other))
    
    def __ge__(self, other):
        return (self.__len__() >= len(other))
    
    # Note that only __radd__ is defined here, because we can't mutate this
    # object's length (but we can add it to another object)
    
    def __radd__(self, other):
        if hasattr(other, '__iter__'):
            result = other.__class__(other)
            result.extend(self)
            return result
        else:
            raise TypeError, "Cannot add a non-iterable to a sequence."
    
    # Only these two non-magic methods are implemented here (technically we could
    # implement reverse and sort since they don't change the length of the sequence,
    # but those look too much like mutating the object itself so we won't).
    
    def index(self, value, start=0, end=0):
        if start < 0:
            start += self.__len__()
        start = inrange(start, 0, self.__len__() - 1)
        if end < 1:
            end += self.__len__()
        end = inrange(end, 0, self.__len__())
        for i in range(start, end):
            if self.__getitem__(i) == value:
                return i
        raise ValueError, "List item not found."
    
    def count(self, value):
        result = 0
        for item in self.__iter__():
            if item == value:
                result += 1
        return result
