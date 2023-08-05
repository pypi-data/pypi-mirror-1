import unittest
import doctest
from anagrammer import anagrammer, convert, lookup, combinations

suite = unittest.TestSuite()
for mod in anagrammer, convert, lookup, combinations:
    suite.addTest(doctest.DocTestSuite(mod))
suite.addTest(doctest.DocFileSuite('anagrammer.txt'))
runner = unittest.TextTestRunner(verbosity=9)
runner.run(suite)
