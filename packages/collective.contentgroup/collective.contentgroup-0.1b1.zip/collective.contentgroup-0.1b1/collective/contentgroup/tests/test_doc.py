"""
This is an integration doctest test. It uses PloneTestCase and doctest
syntax.
"""
from Testing import ZopeTestCase as ztc
from zope.testing import doctestunit
import base
import doctest
import unittest

optionflags = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_ONLY_FIRST_FAILURE
)

def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            'README.txt', 
            package='collective.contentgroup',
            test_class=base.BaseTestCase,
            optionflags=optionflags
        ),
    ])

