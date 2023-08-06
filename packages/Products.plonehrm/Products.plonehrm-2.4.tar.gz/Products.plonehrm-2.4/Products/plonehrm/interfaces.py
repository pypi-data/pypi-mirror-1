__author__ = """Reinout van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from zope.component.interfaces import IObjectEvent
from zope.interface import Interface


class IHRMCheckEvent(IObjectEvent):
    """ An event that is fired at a regular interval
    This can be triggered using a cron job.
    """


class IEmployee(Interface):
    """ Marker interface for an Employee """


class IEmployeeModule(Interface):
    """ Marker interface for an EmployeeModule """


class IWorkLocation(Interface):
    """ Marker interface for a WorkLocation """

class ITemplate(Interface):
    """ Marker interface for a Template """
