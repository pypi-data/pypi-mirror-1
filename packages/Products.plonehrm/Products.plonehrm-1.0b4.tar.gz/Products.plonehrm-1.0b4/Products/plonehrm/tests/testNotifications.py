__author__ = """Maurits van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

try:
    from Products.PloneTestCase.PloneTestCase import USELAYER
    from Products.PloneTestCase.layer import PloneSite
except:
    USELAYER = False

from Products.plonehrm.tests.base import MainTestCase
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


class testOverview(MainTestCase):
    """Test-cases for class(es) ."""
    pass


def test_suite():
    from unittest import TestSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

    s = ZopeDocFileSuite('notifications.txt',
                         optionflags=OPTIONFLAGS,
                         package='Products.plonehrm.doc',
                         test_class=testOverview)
    if USELAYER:
        s.layer = PloneSite
    return TestSuite((s, ))
