#!/usr/bin/env python
"""
TEST_STDLIB_ABSTRACTLIST.PY -- test script for plib.stdlib.baselist
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the abstractlist class.
"""

import unittest

from plib.stdlib import abstractlist

import stdlib_abstract_testlib

class testlist(abstractlist):
    def __init__(self, seq=None):
        self._storage = []
        abstractlist.__init__(self, seq)
    def __len__(self):
        return len(self._storage)
    def __getitem__(self, index):
        result = self._storage[index]
        if isinstance(index, slice):
            result = self.__class__(result)
        return result
    def __setitem__(self, index, value):
        self._storage[index] = value
    def __delitem__(self, index):
        del self._storage[index]

class Test_abstractlist(stdlib_abstract_testlib.MutableSequenceTest):
    type2test = testlist

if __name__ == '__main__':
    unittest.main()
