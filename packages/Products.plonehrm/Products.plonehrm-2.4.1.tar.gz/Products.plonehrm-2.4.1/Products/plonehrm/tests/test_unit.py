import unittest
from zope.testing import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite(
        [doctest.DocFileSuite('doc/plonehrm-technical.txt',
                              optionflags=OPTIONFLAGS,
                              package='Products.plonehrm'),
         doctest.DocTestSuite(module='Products.plonehrm.validator',
                              optionflags=OPTIONFLAGS)])
