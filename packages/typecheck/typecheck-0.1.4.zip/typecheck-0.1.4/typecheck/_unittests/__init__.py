import unittest as _unittest
import doctest as _doctest

from typecheck import doctest_support
import basic, doctests

suite = _unittest.TestSuite()

suite.addTest(_unittest.makeSuite(basic._TestSuite))
suite.addTest(_doctest.DocTestSuite(doctests))
