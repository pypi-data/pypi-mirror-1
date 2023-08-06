import unittest
import doctest
from listcomparator import comparator


def test_doctests():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('../../README.txt'))
    # we have some doc tests in the module
    suite.addTest(doctest.DocTestSuite(comparator))
    runner = unittest.TextTestRunner()
    runner.run(suite)
