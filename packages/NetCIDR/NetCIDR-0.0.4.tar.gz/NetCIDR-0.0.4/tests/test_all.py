import unittest
from doctest import DocTestSuite, DocFileSuite

import sys
sys.path.append('./netcidr')
sys.path.append('../netcidr')
import netcidr

testMods = [
    'netcidr',
    'netcidr.ipmath',
    'netcidr.utils',
    ]

suite = unittest.TestSuite()
tests = [DocTestSuite(x) for x in testMods]
tests.append(DocFileSuite('../README'))
suite.addTests(tests)
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
