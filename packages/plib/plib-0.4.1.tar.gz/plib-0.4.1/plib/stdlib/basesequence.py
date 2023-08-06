#!/usr/bin/env python
"""
Module basesequence
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the basesequence class.
"""

from plib.stdlib import abstractsequence

class basesequence(abstractsequence):
    """
    Base class for sequence with non-mutable length. Forces sequence indexes to
    be integers (or throws ValueError), and throws IndexError if index is out of
    range.
    """
    
    def _get_data(self, index):
        """ Get item by index. """
        raise NotImplementedError
    
    def _set_data(self, index, value):
        """ Set item at index to value. """
        raise NotImplementedError
    
    def _index_ok(self, index):
        if not isinstance(index, int):
            raise TypeError, "Sequence index must be an int."
        if not ((index >= 0) and (index < self.__len__())):
            raise IndexError, "Sequence index out of range."
        return index
    
    def __getitem__(self, index):
        return self._get_data(self._index_ok(index))
    
    def __setitem__(self, index, value):
        self._set_data(self._index_ok(index), value)
