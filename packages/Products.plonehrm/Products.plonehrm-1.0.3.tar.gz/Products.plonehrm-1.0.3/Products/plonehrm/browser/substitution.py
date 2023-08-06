from zope.interface import implements
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFPlone.utils import getSiteEncoding
from plone.app.portlets.portlets import base

from Products.plonehrm.interfaces import IEmployee
from Products.plonehrm.interfaces import IWorkLocation
from Products.plonehrm.browser.interfaces import ISubstitutionPortlet
from Products.plonehrm import PloneHrmMessageFactory as _

from plonehrm.contracts.interfaces import IContract


class BaseSubstitutionView(BrowserView):
    """Substitute some variables or print the available variables.

    Only useful to call on Document-like content types.  It has two uses:

    - When called on a Document within one of the template tools of
      plonehrm modules, like portal_contracts and
      portal_jobperformance, it can list parameters that are available
      for substitution.

    - When called on a child of an Employee (e.g. Contract or
      JobPerformanceInterview), you can substitute variables mentioned
      in those documents.

    Inherit from this in your employee module.
    """

    # override this mapping to localize the substitution terms (yes, one
    # language per site only)
    substitution_translations = {
        '[official_name_employee]': '[official_name_employee]',
        '[gender]': '[gender]',
        '[initials]': '[initials]',
        '[last_name]': '[last_name]',
        '[address_employee]': '[address_employee]',
        '[postal_code_employee]': '[postal_code_employee]',
        '[city_employee]': '[city_employee]',
        '[place_of_birth_employee]': '[place_of_birth_employee]',
        '[date_of_birth_employee]': '[date_of_birth_employee]',
        '[startdate_employee]': '[startdate_employee]',
        '[part_full_time]': '[part_full_time]',
        '[hours_per_week]': '[hours_per_week]',
        '[function]': '[function]',
        '[wages]': '[wages]',
        '[name_worklocation]': '[name_worklocation]',
        '[address_worklocation]': '[address_worklocation]',
        '[city_worklocation]': '[city_worklocation]',
        '[today]': '[today]',
        '[trial_period]': '[trial_period]',
        '[contract_duration]': '[contract_duration]',
    }

    def __init__(self, context, request):
        self.context = aq_inner(context)

        # We're called on a child of an employee. So we need to
        # grab our parent (=employee) and our grandparent
        # (=worklocation).
        self.employee = aq_parent(aq_inner(self.context))
        if not IEmployee.providedBy(self.employee):
            self.employee = None
        self.worklocation = aq_parent(aq_inner(self.employee))
        if not IWorkLocation.providedBy(self.worklocation):
            self.worklocation = None

        # Call an update method.  Now you might only need to override
        # that method when you want to customize this view.
        self.params = self.calcParams()

        # keys is no longer used by calcParams (because it builds a new
        # sorted list), but it does get used for displaying the available
        # terms in the views
        self.keys = self.substitution_translations.values()
        self.keys.sort()

    def calcParams(self):
        """Calculate the values of the parameters for substitution.
        """
        r = {}
        ploneview = self.context.restrictedTraverse('@@plone')

        # We ignore [naam_formule] but make a note of it anyway.
        r['[official_name_employee]'] = self.employee and self.employee.officialName()
        if self.employee:
            gender = self.employee.personal.getGender()
            if gender == 'man':
                gender = 'De Heer'
            elif gender == 'vrouw':
                gender = 'Mevrouw'
        r['[gender]'] = self.employee and gender
        r['[initials]'] = self.employee and self.employee.getInitials()
        r['[last_name]'] = self.employee and (self.employee.getMiddleName() + ' ' +
                                               self.employee.getLastName()).strip()
        r['[address_employee]'] = self.employee and self.employee.personal.getAddress()
        r['[postal_code_employee]'] = self.employee and self.employee.personal.getPostalCode()
        r['[city_employee]'] = self.employee and self.employee.personal.getCity()
        r['[place_of_birth_employee]'] = self.employee and self.employee.personal.getPlaceOfBirth()
        r['[date_of_birth_employee]'] = self.employee and ploneview.toLocalizedTime(self.employee.personal.getBirthDate())

        # Totally skip the contract parameters when you are in the FunctioningTool
        if not 'portal_jobperformance' in self.context.absolute_url():
            contract = self.context
            if not IContract.providedBy(contract):
                contract = None
            r['[startdate_employee]'] = contract and ploneview.toLocalizedTime(contract.getStartdate())
            r['[part_full_time]'] = contract and contract.getEmploymentType()
            r['[hours_per_week]'] = contract and contract.getHours()
            r['[function]'] = contract and contract.getFunction()
            r['[wages]'] = contract and contract.getWage()
            r['[trial_period]'] = contract and contract.getTrialPeriod()
            r['[contract_duration]'] = contract and contract.getDuration()

        # Note: Do something with the CAO?

        r['[name_worklocation]'] = self.worklocation and self.worklocation.getOfficialName()
        r['[address_worklocation]'] = self.worklocation and '<br />'.join(self.worklocation.getAddress())
        r['[city_worklocation]'] = self.worklocation and self.worklocation.getCity()

        r['[today]'] = ploneview.toLocalizedTime(DateTime())

        return r
    
    def substitute(self, text):
        keytuples = self.substitution_translations.items()
        # We will reverse the keys as otherwise $NAME would also match
        # $NAMELIST or so.
        # Actually, we switched to [name] so that would never match
        # [namelist], but let's keep this reversal for those who prefer
        # their paramaters prefixed with a dollar sign.
        keytuples.sort(key=lambda a: -len(a[1]))

        encoding = getSiteEncoding(self.context)
        for key, translated_key in keytuples:
            value = self.params[key]
            if isinstance(value, unicode):
                value = value.encode(encoding)
            if not isinstance(value, str):
                # e.g. an integer
                value = str(value)
            text = text.replace(translated_key, value)
        return text


class Assignment(base.Assignment):
    implements(ISubstitutionPortlet)

    @property
    def title(self):
        return _(u"Available parameters")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('parameters.pt')

    @property
    def available(self):
        """Should the portlet be shown?

        Portlet is available when there are keys.

        They are only handy for showing when viewing (editing really)
        a Document within portal_jobperformance or portal_contracts.
        """
        url = self.context.absolute_url()
        tool_ids = ('portal_jobperformance', 'portal_contracts')
        for tool_id in tool_ids:
            if tool_id in url:
                if url.split('/')[-1] != tool_id:
                    return len(self.keys) > 0
                return False
        return False

    def render(self):
        return self._template()

    @property
    def keys(self):
        context = aq_inner(self.context)
        view = context.restrictedTraverse('@@substituter')
        return view.keys


class AddForm(base.AddForm):
    form_fields = form.Fields(ISubstitutionPortlet)
    label = _(u"Add Substitution parameters Portlet")
    description = _(u"This portlet displays substitution parameters.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(ISubstitutionPortlet)
    label = _(u"Edit Substitution parameters Portlet")
    description = _(u"This portlet displays substitution parameters.")
