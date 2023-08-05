#!/usr/bin/env python
"""
Module baselist
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the baselist class.
"""

from plib.stdlib import normalize, normalize_slice, abstractlist

class baselist(abstractlist):
    """
    Base list class that partially implements the necessary abstract methods.
    
    This base class reduces the amount of work required to make a data structure
    look like a Python list. It implements the __getitem__, __setitem__,
    and __delitem__ methods to provide the following:
    
    -- normalization of indexes (negative indexes relative to end of list and out
       of range exceptions)
    
    -- support for slices as arguments
    
    The work needed to fully implement a list-emulator is thus reduced to the
    following: implement _get_data to retrieve a single item by index, _set_data
    to store a single item by index, _add_data to add/insert a single item by
    index, and _del_data to remove a single item by index. Implementing these
    methods is sufficient to overlay full list functionality on the underlying
    data structure; operations which add, set, or remove multiple items will
    result in multiple calls to _set, _add, or _del as appropriate. Other
    methods can be overridden if needed for efficiency (e.g., to increase speed
    for multi-item operations), per the abstractlist class docstring (note that,
    as that docstring states, __init__ will almost always need to be overridden to
    initialize the underlying data structure, and sort must be implemented if
    sorting functionality is desired).
    """
    
    def _get_data(self, index):
        """ Return a single item by index (slice arguments to __getitem__ will
        result in multiple calls to this method). """
        
        raise NotImplementedError
    
    def _set_data(self, index, value):
        """ Store a single item by index (slice arguments to __setitem__ may
        result in multiple calls to this method). This method should never be
        called with an index outside the list range (appending items should be
        done by _add_data below), and it should always replace the data at index
        with value, not insert a new item (that's also done by _add_data). """
        
        raise NotImplementedError
    
    def _add_data(self, index, value):
        """ Insert a single item at index (zero-length slice arguments to
        __setitem__ will result in one call to this method for each item
        in the value being set). If index == self.__len__(), this method
        should append value to the list. """
        
        raise NotImplementedError
    
    def _del_data(self, index):
        """ Delete a single item by index (slice arguments to __delitem__ will
        result in multiple calls to this method). """
        
        raise NotImplementedError
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return self._get_data(normalize(self.__len__(), index))
        
        elif isinstance(index, slice):
            result = self.__class__()
            indexes = normalize_slice(self.__len__(), index)
            
            # The only case we worry about here is a non-empty slice
            # (an empty slice will not be an iterator) -- things will
            # get much more interesting in __setitem__ below.
            if hasattr(indexes, '__iter__'):
                for i in indexes:
                    result.append(self._get_data(i))
            return result
        
        else:
            raise TypeError, "List index must be an int or a slice."
    
    def __setitem__(self, index, value):
        if isinstance(index, int):
            self._set_data(normalize(self.__len__(), index), value)
        
        elif isinstance(index, slice):
            if not hasattr(value, '__iter__'):
                raise ValueError, "Cannot assign a non-iterable to a slice."
            
            # Here things get kind of hairy because there are several
            # cases to consider.
            norm = normalize_slice(self.__len__(), index)
            
            if isinstance(norm, int):
                # Slice of form [n:n], meaning insert value (if n within
                # list) or append value (if n at end)
                if index.step is not None:
                    # Explicit step values are not allowed if inserting/appending
                    raise ValueError, "Step cannot be specified if inserting/appending."
                
                else:
                    # Insert/append (_add_data will handle both cases below)
                    indexes = range(norm, norm + len(value))
            
            else:
                # Slice of form [n:m] where n != m
                if (len(norm) < len(value)) and (norm[-1] == (self.__len__() - 1)):
                    
                    # Slice goes past end of list, check step
                    if index.step is not None:
                        # Explicit step values are not allowed if extending list
                        raise ValueError, "Step cannot be specified if extending sequence."
                    
                    else:
                        # Extend the list to include all value items
                        indexes = range(norm[0], norm[0] + len(value))
                
                else:
                    # Here we need to check if the lengths are equal
                    indexes = norm
                    if len(indexes) != len(value):
                        raise ValueError, "Value must be the same length as slice."
            
            # Now do the operation (note that we have to use zip here, not
            # enumerate, because the indexes might not start at zero)
            for i, ivalue in zip(indexes, value):
                
                if (not isinstance(norm, int)) and (i < self.__len__()):
                    # Not past end of list and not inserting
                    self._set_data(i, ivalue)
                
                else:
                    # Inserting or appending
                    self._add_data(i, ivalue)
        
        else:
            raise TypeError, "List index must be an int or a slice."
    
    def __delitem__(self, index):
        if isinstance(index, int):
            self._del_data(normalize(self.__len__(), index))
        
        elif isinstance(index, slice):
            indexes = normalize_slice(self.__len__(), index)
            
            # Here again we're only interested in deleting non-empty
            # slices.
            if hasattr(indexes, '__iter__'):
                for i in indexes:
                    self._del_data(i)
        
        else:
            raise TypeError, "List index must be an int or a slice."
