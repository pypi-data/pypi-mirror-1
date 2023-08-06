import unittest
from Testing import ZopeTestCase as ztc
from zope.testing import doctest
from plonehrm.absence.tests.base import BaseTestCase


def test_suite():
    return unittest.TestSuite([
        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
                'docs/absence.txt', package='plonehrm.absence',
                test_class=BaseTestCase),
        ztc.ZopeDocFileSuite(
                'docs/checker.txt', package='plonehrm.absence',
                test_class=BaseTestCase),
        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
