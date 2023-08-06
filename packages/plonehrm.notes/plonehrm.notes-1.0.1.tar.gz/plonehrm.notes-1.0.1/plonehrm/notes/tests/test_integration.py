import unittest
from zope.testing import doctest
from Testing import ZopeTestCase as ztc
from plonehrm.notes.tests.base import BaseTestCase

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
                'browser.txt', package='plonehrm.notes.tests',
                test_class=BaseTestCase),
        ])
