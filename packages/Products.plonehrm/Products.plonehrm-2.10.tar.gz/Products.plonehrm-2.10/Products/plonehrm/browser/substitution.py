from zope.interface import implements
from zope.i18n import translate
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner, aq_parent, aq_chain
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
        '[company_address]': '[company_address]',
        '[company_city]': '[company_city]',
        '[company_legal_name]': '[company_legal_name]',
        '[company_postal_code]': '[company_postal_code]',
        '[contract_days_per_week]': '[contract_days_per_week]',
        '[contract_duration]': '[contract_duration]',
        '[contract_expirydate]': '[contract_expirydate]',
        '[contract_function]': '[contract_function]',
        '[contract_hours_per_week]': '[contract_hours_per_week]',
        '[contract_part_full_time]': '[contract_part_full_time]',
        '[contract_startdate]': '[contract_startdate]',
        '[contract_trial_period]': '[contract_trial_period]',
        '[contract_wage]': '[contract_wage]',
        '[employee_address]': '[employee_address]',
        '[employee_city]': '[employee_city]',
        '[employee_date_of_birth]': '[employee_date_of_birth]',
        '[employee_first_name]': '[employee_first_name]',
        '[employee_full_name]': '[employee_full_name]',
        '[employee_initials]': '[employee_initials]',
        '[employee_last_name]': '[employee_last_name]',
        '[employee_official_name]': '[employee_official_name]',
        '[employee_place_of_birth]': '[employee_place_of_birth]',
        '[employee_postal_code]': '[employee_postal_code]',
        '[employee_title]': '[employee_title]',
        '[first_contract_startdate]': '[first_contract_startdate]',
        '[previous_contract_startdate]': '[previous_contract_startdate]',
        '[today]': '[today]',
        '[worklocation_address]': '[worklocation_address]',
        '[worklocation_city]': '[worklocation_city]',
        '[worklocation_pay_period]': '[worklocation_pay_period]',
        '[worklocation_postal_code]': '[worklocation_postal_code]',
        '[worklocation_trade_name]': '[worklocation_trade_name]',
        '[worklocation_vacation_days]': '[worklocation_vacation_days]',
        '[worklocation_contactperson]': '[worklocation_contactperson]'
        }

    # For migration.  See
    # Products.plonehrm.migration.replace_old_substitution_parameters
    old_parameters = {
        # old: new
        '[company_official_name]': '[company_legal_name]',
        }

    def __init__(self, context, request):
        self.context = aq_inner(context)

        # We're called on a child of an employee. So we need to
        # grab our parent (=employee) and our grandparent
        # (=worklocation).
        self.employee = self.get_employee()
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

    def get_employee(self):
        """Get the employee that this context is in.

        Note that we probably are in the portal_factory, so our direct
        parent is not an Employee.  But we can traverse up the
        acquisition chain to find it.  Or there may be other reasons
        why the employee is not our parent, but e.g. our grand parent.
        """
        context = aq_inner(self.context)
        for parent in aq_chain(context):
            if IEmployee.providedBy(parent):
                return parent

    def calcParams(self):
        """Calculate the values of the parameters for substitution.
        """
        r = {}
        ploneview = self.context.restrictedTraverse('@@plone')
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        language = pps.default_language()

        # We ignore [naam_formule] but make a note of it anyway.
        r['[employee_official_name]'] = self.employee and \
            self.employee.officialName()
        if self.employee:
            gender = self.employee.getGender()
            # Now try to translate the gender.  Note that there might
            # be old values that are not in the current DisplayList.
            # Just display those literally.
            vocabulary = self.employee._genderVocabulary()
            value = vocabulary.getValue(gender)
            if value:
                gender = translate(value, target_language=language)

            # We compute the employe initials.
            initials = self.employee.getInitials()
            if not initials:
                fnames = self.employee.getFirstName().split(' ')
                for fname in fnames:
                    if len(fname):
                        initials += fname[0] + '.'

            # We compute the first contract start date.
            first_contract_startdate = self.employee.getWorkStartDate()
            if not first_contract_startdate:
                content_filter = {'portal_type': 'Contract'}
                contracts = self.employee.getFolderContents(
                    contentFilter=content_filter)

                for contract in [c.getObject() for c in contracts]:
                    if contract.getStartdate() < first_contract_startdate or \
                       not first_contract_startdate:
                        first_contract_startdate = contract.getStartdate()

            first_contract_startdate = ploneview.toLocalizedTime(
                first_contract_startdate)
                
                
        r['[employee_title]'] = self.employee and gender
        r['[employee_initials]'] = self.employee and initials
        r['[employee_first_name]'] = self.employee and \
            self.employee.getFirstName()
        r['[employee_full_name]'] = self.employee and \
            self.employee.Title()
        r['[employee_last_name]'] = self.employee and (
            self.employee.getMiddleName() + ' ' +
            self.employee.getLastName()).strip()
        r['[employee_address]'] = self.employee and self.employee.getAddress()
        r['[employee_postal_code]'] = self.employee and \
            self.employee.getPostalCode()
        r['[employee_city]'] = self.employee and self.employee.getCity()
        r['[employee_place_of_birth]'] = self.employee and \
            self.employee.getPlaceOfBirth()
        r['[employee_date_of_birth]'] = self.employee and \
            ploneview.toLocalizedTime(self.employee.getBirthDate())

        # Totally skip the contract parameters when you are in the
        # FunctioningTool        
        if self.context.Type() in ['Contract', 'Letter']:
            contract = self.context
            if not IContract.providedBy(contract):
                contract = None
            r['[contract_startdate]'] = contract and ploneview.toLocalizedTime(
                contract.getStartdate())
            r['[contract_part_full_time]'] = contract and \
                contract.getEmploymentType()
            r['[contract_hours_per_week]'] = contract and contract.getHours()
            r['[contract_days_per_week]'] = contract \
                and contract.getDaysPerWeek()
            r['[contract_function]'] = contract and contract.getFunction()
            r['[contract_wage]'] = contract and contract.getWage()
            r['[contract_trial_period]'] = contract and \
                contract.getTrialPeriod()
            r['[contract_duration]'] = contract and contract.getDuration()
            r['[contract_expirydate]'] = contract and contract.expiry_date() \
                and ploneview.toLocalizedTime(contract.expiry_date())

            previous_contract = contract and contract.base_contract()
            r['[previous_contract_startdate]'] = previous_contract and \
                ploneview.toLocalizedTime(previous_contract.getStartdate())

        # Note: Do something with the CAO?

        # Start date
        r['[first_contract_startdate]'] = self.employee and \
                                          first_contract_startdate

        # Work Location:
        r['[worklocation_trade_name]'] = self.worklocation and \
            self.worklocation.Title()
        r['[worklocation_address]'] = self.worklocation and \
            self.worklocation.getAddress()
        r['[worklocation_postal_code]'] = self.worklocation and \
            self.worklocation.getPostalCode()
        r['[worklocation_city]'] = self.worklocation and \
            self.worklocation.getCity()

        if self.worklocation:
            pay_period = self.worklocation.getPayPeriod()
            vocabulary = self.worklocation._payPeriodVocabulary()
            value = vocabulary.getValue(pay_period)
            if value:
                pay_period = translate(value, target_language=language)
        r['[worklocation_pay_period]'] = self.worklocation and pay_period
        r['[worklocation_vacation_days]'] = self.worklocation and \
            self.worklocation.getVacationDays()

        r['[worklocation_contactperson]'] = self.worklocation and \
            self.worklocation.getContactPerson()

        # Company:
        r['[company_legal_name]'] = self.worklocation and \
            self.worklocation.getOfficialName()
        r['[company_address]'] = self.worklocation and \
            self.worklocation.getCompanyAddress()
        r['[company_postal_code]'] = self.worklocation and \
            self.worklocation.getCompanyPostalCode()
        r['[company_city]'] = self.worklocation and \
            self.worklocation.getCompanyCity()

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
            if key in self.params:
                value = self.params[key]
                if isinstance(value, unicode):
                    value = value.encode(encoding)
                if value is None:
                    value = '&hellip;'
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
