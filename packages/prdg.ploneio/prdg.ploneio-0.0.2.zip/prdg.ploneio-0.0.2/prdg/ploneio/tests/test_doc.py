"""
This is an integration doctest test. It uses PloneTestCase and doctest
syntax.
"""
import unittest
import doctest

from zope.testing import doctestunit
from Testing import ZopeTestCase as ztc

import base

optionflags = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_ONLY_FIRST_FAILURE
)

def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            'README.txt', 
            package='prdg.ploneio',
            test_class=base.BaseTestCase,
            optionflags=optionflags
        ),
    ])

