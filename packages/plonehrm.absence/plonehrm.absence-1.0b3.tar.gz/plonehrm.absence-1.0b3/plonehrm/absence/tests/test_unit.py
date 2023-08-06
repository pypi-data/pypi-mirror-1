import doctest
import unittest
from zope.testing import doctestunit

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='plonehrm.absence',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocFileSuite(
            'docs/absence.txt',
            package='plonehrm.absence',
            optionflags=optionflags),

        doctestunit.DocFileSuite(
            'docs/checker.txt',
            package='plonehrm.absence',
            optionflags=optionflags),

        #doctestunit.DocTestSuite(
        #    module='plonehrm.absence.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='plonehrm.absence',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='plonehrm.absence',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
