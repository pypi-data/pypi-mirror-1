from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.interface import Interface, implements
from zope.viewlet.interfaces import IViewlet

from Products.plonehrm import utils
from Products.plonehrm import PloneHrmMessageFactory as _
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
    """Return the phone number of the current employee"""
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
    """Return the mobile number of the current employee"""
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

class AddressView(Explicit):
    """Return the address of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Address'

    def render(self):
        return self.context.getAddress()

class ZipCodeView(Explicit):
    """Return the zip code of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'ZipCode'

    def render(self):
        return self.context.getPostalCode()

class CityView(Explicit):
    """Return the city of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'City'

    def render(self):
        return self.context.getCity()


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

    def is_arbo(self):
        """ Checks if the user has Arbo manager rights.
        """
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission('plonehrm: manage Arbo content',
                                          self.context)
    def render(self):
        absence_html = u''
        if self.is_sick():
            days = self.days_absent()
            if days == 1:
                absence = _('1_day_absent',
                            default=u'(1 day absent)')
            else:
                absence = _(u'x_days_absent',
                            default=u'(${days} days absent)',
                            mapping={'days': days})
            absence = translate(absence, context=self.request)
            absence_html = '<span class="absencetext">%s</span>' % absence

        link_html = '<a href="%s">%s</a>' % (
            self.context.absolute_url(),
            self.context.Title())
        return u' '.join([link_html, absence_html])

    def is_sick(self):
        if IAbsenceAdapter is None:
            return False
        absences = IAbsenceAdapter(self.context)
        return bool(absences.current_absence())

    def days_absent(self):
        if IAbsenceAdapter is None or not self.is_sick():
            return None
        absences = IAbsenceAdapter(self.context)
        absence = absences.current_absence()
        return absence.days_absent(self.is_arbo())
