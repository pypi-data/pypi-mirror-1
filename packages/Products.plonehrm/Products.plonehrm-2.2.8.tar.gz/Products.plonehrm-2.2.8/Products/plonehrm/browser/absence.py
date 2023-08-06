from Acquisition import Explicit
from Products.plonehrm import PloneHrmMessageFactory as _
from zope.i18n import translate
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
try:
    from plonehrm.absence.absence import IAbsenceAdapter
except ImportError:
    IAbsenceAdapter = None


class AbsenceView(Explicit):
    """Return the number of sick days of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Number of sickdays'

    def render(self):
        if self.is_sick():
            days = self.days_absent()
        return [days, days]
