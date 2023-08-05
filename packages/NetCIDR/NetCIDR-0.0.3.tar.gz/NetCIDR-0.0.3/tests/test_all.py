import unittest
import doctest

import sys
sys.path.append('./lib')
sys.path.append('../lib')
import netcidr

test_mods = ['netcidr.network']

suite = unittest.TestSuite()
for mod in test_mods:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner()
runner.run(suite)
