#! /usr/bin/env python
"""
RUNTESTS.PY -- standard test script
Copyright (C) 2008-2009 by Peter A. Donis

Released under the Python Software Foundation License

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
    result.append(unittest.defaultTestLoader.loadTestsFromModule(mod))
    return result

def run_tests():
    doctests = glob.glob("test_*.txt")
    if doctests:
        print "Running doctests..."
        for filename in doctests:
            run_doctest(filename)
    else:
        print "No doctests found."
    unittests = []
    for filename in glob.glob("test_*.py"):
        unittests.extend(get_unittests(os.path.splitext(os.path.basename(filename))[0]))
    if unittests:
        print "Running unittests..."
        suite = unittest.TestSuite(unittests)
        runner = unittest.TextTestRunner(verbosity=verbosity)
        runner.run(suite)
    else:
        print "No unittests found."

if __name__ == '__main__':
    # TODO: set module_relative and verbosity from command line options
    run_tests()
