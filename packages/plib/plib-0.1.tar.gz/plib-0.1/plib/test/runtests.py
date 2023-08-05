#!/usr/bin/env python
"""
RUNTESTS.PY -- standard test script
Copyright (C) 2008 by Peter A. Donis

Boilerplate test running script. Looks for
the following test files in the directory
of the script file:

-- test_*.txt files are run as doctests
-- test_*.py files are run as unit tests
"""

import sys
import os
import glob
import doctest
import unittest

module_relative = False
verbosity = 0

def run_doctest(filename):
    doctest.testfile(filename, module_relative=module_relative)

def get_unittests(pyname):
    result = []
    mod = __import__(pyname)
    for attrname in dir(mod):
        obj = getattr(mod, attrname)
        try:
            if issubclass(obj, (unittest.TestCase, unittest.TestSuite)):
                result.append(obj())
        except TypeError:
            pass
    return result

def run_tests():
    for filename in glob.glob("test_*.txt"):
        run_doctest(filename)
    tests = []
    for filename in glob.glob("test_*.py"):
        tests.extend(get_unittests(os.path.splitext(os.path.basename(filename))[0]))
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

if __name__ == '__main__':
    # TODO: set module_relative and verbosity from command line options
    run_tests()
