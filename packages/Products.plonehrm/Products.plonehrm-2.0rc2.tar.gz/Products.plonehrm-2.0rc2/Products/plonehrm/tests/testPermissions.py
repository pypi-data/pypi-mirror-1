from Products.plonehrm.tests.base import MainTestCase


def test_suite():
    from unittest import TestSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

    s = ZopeDocFileSuite('permissions.txt',
                         package='Products.plonehrm.doc',
                         test_class=MainTestCase)
    return TestSuite((s, ))
