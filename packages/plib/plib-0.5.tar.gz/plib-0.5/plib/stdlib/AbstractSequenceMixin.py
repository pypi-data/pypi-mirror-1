#!/usr/bin/env python
"""
Module AbstractSequenceMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AbstractSequenceMixin class.
"""

from plib.stdlib import AbstractContainerMixin

class AbstractSequenceMixin(AbstractContainerMixin):
    """
    Mixin class for fixed-length abstract sequence classes to
    support argument checking on item assignment, enforcing the
    rule that the sequence's length cannot change.
    """
    
    def _set_data(self, index, value):
        """ Store a single item by index (slice arguments to __setitem__ may
        result in multiple calls to this method). """
        raise NotImplementedError
    
    def __setitem__(self, index, value):
        extended = isinstance(index, slice) and (index.step is not None)
        index = self._index_ok(index)
        if isinstance(index, tuple):
            try:
                vlength = len(value)
            except TypeError:
                try:
                    vlength = len(list(value)) # TODO: can we avoid realizing generators/iterators here?
                except TypeError:
                    raise TypeError, "can only assign an iterable"
            length, index = index
            if (length < 1) and not extended:
                if vlength != 0:
                    self._add_items(index, value)
            elif length != vlength:
                if extended:
                    raise ValueError("attempt to assign sequence of length %i to extended slice of length %i" %
                        (vlength, length))
                self._rep_items(index, value)
            else:
                for i, v in zip(index, value):
                    self._set_data(i, v)
        else:
            self._set_data(index, value)
    
    # These methods allow easy factoring out of the differences
    # between fixed-length and fully mutable sequences
    
    def _add_items(self, index, value):
        raise TypeError, "object does not support item insert/append"
    
    def _rep_items(self, indexes, value):
        raise ValueError, "object length cannot be changed"
