#!/usr/bin/env python
"""
Module abstractcontainer
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

This module contains the abstractcontainer class.
"""

class abstractcontainer(object):
    """
    An abstract class to provide the minimal possible support of the
    Python container protocol. Subclasses can implement just the __len__
    and __getitem__ methods to allow the class to be used in the standard
    Python container idioms like for item in container, etc. This
    container is immutable, so its length and its items cannot be
    changed (increasing levels of mutability are provided by the
    abstractsequence and abstractlist classes); note that this does
    *not* mean the underlying data structure must be immutable, only
    that the view of it provided by this container class is.
    """
    
    def __len__(self):
        """ Return the number of items in the list. """
        raise NotImplementedError
    
    def __getitem__(self, index):
        """
        Get item by index. Negative indexes are relative to end of list.
        Raise IndexError if index is out of range.
        """
        raise NotImplementedError
    
    def __iter__(self):
        for index in range(self.__len__()):
            yield self.__getitem__(index)
    
    def __contains__(self, value):
        for item in self.__iter__():
            if item == value:
                return True
        return False
