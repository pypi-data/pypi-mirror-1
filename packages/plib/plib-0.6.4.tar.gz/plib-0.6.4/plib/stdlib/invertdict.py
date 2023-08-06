#!/usr/bin/env python
"""
Module invertdict
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the invertdict class.
"""

import sys

class invertdict(dict):
    """
    Dict with an inverted method added, returns the inverse dict.
    (Note that the returned dict will actually be the same class
    as the instance the invert method is called on.)
    
    Note that we use a generator expression and iteritems to avoid
    making an extra in-memory copy of our data (for the intermediate
    sequence of inverted value, key tuples). Since this only works
    in Python 2.4 and later, an alternate (slower) implementation is
    given for earlier versions.
    """
    
    if sys.version_info < (2, 4):
        
        def inverted(self, keylist=None):
            result = self.__class__()
            if keylist is not None:
                for key in keylist:
                    result[self[key]] = key
            else:
                for key, value in self.iteritems():
                    result[value] = key
            return result
    else:
        
        def inverted(self, keylist=None):
            if keylist is not None:
                return self.__class__((self[key], key) for key in keylist)
            else:
                return self.__class__((value, key) for key, value in self.iteritems())
