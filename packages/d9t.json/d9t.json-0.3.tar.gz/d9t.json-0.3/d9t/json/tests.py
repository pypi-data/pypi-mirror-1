# *-* coding: utf-8 *-*
"""
Test runner for 'd9t.json'.
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def setUp(test):
    pass

def tearDown(test):
    pass

suite = unittest.TestSuite()
suite.addTest(
    doctest.DocFileSuite(
        'README.txt',
        setUp=setUp,
        tearDown=tearDown,
        optionflags=optionflags,
    ),
)

