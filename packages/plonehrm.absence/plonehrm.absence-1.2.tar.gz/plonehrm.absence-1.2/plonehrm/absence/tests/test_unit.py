import doctest
import unittest

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    return unittest.TestSuite([
            doctest.DocTestSuite(
                module='plonehrm.absence.content.note',
                optionflags=optionflags),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
