"""Module to read in all the doctests from src that we want to test.

This module is designed so that "python setup.py test" can just look in
here and automatically suck in the other doctests from the source.
"""

import unittest, doctest
import superpy
from superpy.core import Process, DataStructures
import _test

def MakeMainSuperpyDoctest():
    """Return a unittest.TestSuite object representing doctests from source code

>>> import unitTestsFromSrc
>>> t = unitTestsFromSrc.MakeMainSuperpyDoctest()
>>> t.debug()
    """
    suite = unittest.TestSuite()

    for t in [DataStructures, superpy, Process, _test]:
        testCase = doctest.DocTestSuite(t)
        suite.addTest(testCase)

    return suite

mainTestSuite = MakeMainSuperpyDoctest()
