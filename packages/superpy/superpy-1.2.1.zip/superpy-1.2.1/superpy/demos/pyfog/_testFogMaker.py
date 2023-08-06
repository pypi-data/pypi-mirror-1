"""Module to create test suite to test fog maker.

This lets you test things by doing something like

  "python setup.py test -m superpy.demos.pyfog._testFogMaker"

from the top-level directory.
"""


import unittest, doctest, fogMaker

test_suite = unittest.TestSuite()
test_suite.addTest(doctest.DocTestSuite(fogMaker))
