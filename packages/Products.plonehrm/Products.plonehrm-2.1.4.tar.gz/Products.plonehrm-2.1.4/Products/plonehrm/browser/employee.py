from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch
from Products.Five import BrowserView
from zope.interface import Interface, implements
from zope.viewlet.interfaces import IViewlet
from Products.plonehrm import utils
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
try:
    from plonehrm.absence.absence import IAbsenceAdapter
except ImportError:
    IAbsenceAdapter = None


class IPersonalDataView(Interface):
    pass


class PersonalDataView(Explicit):
    """Viewlet that renders the personal data

    Shown within the employee viewlet manager.
    """
    implements(IViewlet)
    render = ViewPageTemplateFile('personaldata.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def age(self):
        return utils.age(self.context)


class PhoneView(Explicit):
    """Return the fullname of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Phone'

    def render(self):
        return self.context.getTelephone()


class MobileView(Explicit):
    """Return the fullname of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Mobile'

    def render(self):
        return self.context.getMobilePhone()


class EmployeeView(BrowserView):

    @property
    def extraItems(self):
        all = self.context.getFolderContents()
        # Filter out the employee module items.
        moduleTypes = []
        portal_props = getToolByName(self.context,
                                     'portal_properties', None)
        if portal_props is not None:
            hrm_props = getattr(portal_props, 'plonehrm_properties', None)
            if hrm_props is not None:
                moduleTypes = hrm_props.getProperty(
                    'employee_module_portal_types', ())
        rest = [item for item in all
                 if item['portal_type'] not in moduleTypes]
        # Turn 'rest' into a batch for the benefit of the tabular folder
        # macro.
        b_start = 0
        b_size = 1000
        rest = Batch(rest, b_size, b_start, orphan=0)
        return rest


class FullnameView(Explicit):
    """Return the fullname of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Fullname'

    def render(self):
        klass = self.is_sick() and 'employee_sick' or 'employee_healthy'
        return '<a class="%s" href="%s">%s</a>' % (
               klass,
               self.context.getId(),
               self.context.Title())

    def is_sick(self):
        if IAbsenceAdapter is None:
            return False
        absences = IAbsenceAdapter(self.context)
        return bool(absences.current_absence())
