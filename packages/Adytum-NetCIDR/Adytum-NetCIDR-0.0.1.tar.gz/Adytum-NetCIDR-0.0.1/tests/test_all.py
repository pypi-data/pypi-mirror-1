import unittest
import doctest

import sys
sys.path.append('./lib')
sys.path.append('../lib')
import network

test_mods = ['network']

suite = unittest.TestSuite()
for mod in test_mods:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner()
runner.run(suite)
