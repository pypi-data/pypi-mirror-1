from Products.plonehrm.tests.base import MainTestCase
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    from unittest import TestSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

    s = ZopeDocFileSuite('overview.txt',
                         package='Products.plonehrm.doc',
                         optionflags=OPTIONFLAGS,
                         test_class=MainTestCase)
    return TestSuite((s, ))
