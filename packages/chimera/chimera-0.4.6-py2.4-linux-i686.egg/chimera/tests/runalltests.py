#!/usr/bin/python2.4
#
# Runs all tests in the current directory
#
# Execute like:
#   python runalltests.py
#
# Alternatively use the testrunner:
#   python /path/to/Zope/utilities/testrunner.py -qa
#

import os, sys
import doctest
import unittest

# IF YOU ARE NOT GETTING THE RESULTS YOU EXPECT WHILE TESTING
# THIS IS THE LIKELY CAUSE
# :: Use distutils to modify the pythonpath for inplace testing
from distutils.util import get_platform
plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
build_platlib = os.path.join("build", 'lib' + plat_specifier)
test_lib = os.path.join(os.path.abspath(".."), build_platlib)
sys.path.insert(0, test_lib)
# END PATH ADJUSTMENT CODE


TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

#tests = os.listdir(os.curdir)
#tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]
tests = [
    'test_snippets',
    'test_pangocairo',
    'test_svg',
    'test_doctest',
    'test_chimera',
    ]

for test in tests:
    m = __import__(test)
    if hasattr(m, 'test_suite'):
        suite.addTest(m.test_suite())

def main():
    TestRunner(verbosity=1).run(suite)

if __name__ == '__main__':
    main()

