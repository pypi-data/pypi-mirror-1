from zope.interface import Interface, Attribute
from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletDataProvider


class IEmployeeView(Interface):

    def extraItems():
        """ Return all non hrm specific items
        """


class IWorkLocationView(Interface):

    def alternative_views():
        """List of dictionaries with url, title to alternative views.
        """

    def active_employees():
        """Return list of active employees.
        """

    def inactive_employees():
        """Return list of inactive employees.
        """


class IWorkLocationState(Interface):

    def is_worklocation():
        """Return whether the current context is a worklocation."""

    def current_worklocation():
        """Return the worklocation in the acquisition chain."""

    def in_worklocation():
        """Return if there is a worklocation in the acquisition chain."""

    def all_worklocations():
        """Return the brains of all available worklocations."""


class ISubstitutionView(Interface):

    params = Attribute("Keys and substitution values")
    keys = Attribute("Keys available for substitution")


class ISubstitutionPortlet(IPortletDataProvider):
    pass


class IEmployeeDetails(IViewletManager):
    """A viewlet manager that renders all viewlets registered by extension
    modules.
    """


class IEmployeesOverview(IViewletManager):
    """A viewlet manager that renders all viewlets registered by extension
    modules.
    """
