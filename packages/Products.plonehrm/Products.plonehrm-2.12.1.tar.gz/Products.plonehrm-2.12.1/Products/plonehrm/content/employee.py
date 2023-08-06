__author__ = """Reinout van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from datetime import date, timedelta

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import ComputedField
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import ImageWidget
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.utils import safe_unicode
from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm import config
from Products.plonehrm.interfaces import IEmployee
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from persistent import Persistent



schema = Schema((
    StringField(
        name='employeeNumber',
        widget=StringWidget(
            label=_(u'label_employeeNumber', default=u'Employee number'),
        ),
    ),
    StringField(
        name='firstName',
        widget=StringWidget(
            label=_(u'plonehrm_label_firstName', default=u'Firstname'),
        ),
    ),
    StringField(
        name='middleName',
        widget=StringWidget(
            label=_(u'plonehrm_label_middleName', default=u'Middle name'),
        ),
    ),
    StringField(
        name='lastName',
        widget=StringWidget(
            label=_(u'plonehrm_label_lastName', default=u'Last name'),
        ),
        required=1
    ),
    StringField(
        name='initials',
        widget=StringWidget(
            label=_(u'plonehrm_label_initials', default=u'Initials'),
        )
    ),
    StringField(
        name='address',
        widget=StringWidget(
            label=_(u'label_address', default='Address'),
        ),
    ),
    StringField(
        name='postalCode',
        widget=StringWidget(
            label=_(u'label_postalCode', default=u'Postalcode'),
        ),
    ),
    StringField(
        name='city',
        widget=StringWidget(
            label=_(u'label_city', default=u'City'),
        ),
    ),
    StringField(
        name='state',
        widget=StringWidget(
            label=_(u'label_state', default=u'State/Province'),
        ),
    ),
    StringField(
        name='country',
        widget=StringWidget(
            label=_(u'label_country', default=u'Country'),
        ),
    ),
    StringField(
        name='telephone',
        widget=StringWidget(
            label=_(u'label_telephone', default=u'Phone'),
        ),
    ),
    StringField(
        name='mobilePhone',
        widget=StringWidget(
            label=_(u'label_mobilePhone', default=u'Mobilephone'),
        ),
    ),
    StringField(
        name='email',
        widget=StringWidget(
            label=_(u'label_email', default=u'Email'),
        ),
    ),
    DateTimeField(
        name='birthDate',
        required=0,
        validators=("isDateBeforeToday", "checkIfTooYoung"),
        widget=CalendarWidget(
            starting_year=1940,
            show_hm=0,
            label=_(u'label_birthDate', default=u'Birth date'),
        ),
    ),
    StringField(
        name='placeOfBirth',
        widget=StringWidget(
            label=_(u'label_placeOfBirth', default=u'Place of birth'),
        ),
    ),
    StringField(
        name='gender',
        widget=SelectionWidget(
            format="select",
            label=_(u'label_gender', default=u'Gender'),
        ),
        vocabulary='_genderVocabulary'
    ),
    StringField(
        name='civilStatus',
        widget=SelectionWidget(
            format="select",
            label=_(u'label_civilStatus', default=u'Civil status'),
        ),
        vocabulary='_civilStatusVocabulary'
    ),
    StringField(
        name='idType',
        widget=SelectionWidget(
            format="select",
            label=_(u'label_idType', default=u'Type of ID'),
        ),
        vocabulary='_idTypeVocabulary'
    ),
    StringField(
        name='idNumber',
        widget=StringWidget(
            label=_(u'label_idNumber', default=u'ID number'),
        ),
    ),
    DateTimeField(
        name='idEndDate',
        widget=CalendarWidget(
            show_hm=0,
            starting_year=2007,
            label=_(u'label_idEndDate', default=u'Expiration date'),
        ),
    ),
    StringField(
        name='nationality',
        widget=StringWidget(
            label=_(u'label_nationality', default=u'Nationality'),
        ),
    ),
    StringField(
        name='socialSecurityNumber',
        validators=("isBSNValid"),
        widget=StringWidget(
            label=_(u'label_socialSecurityNumber',
                    default=u'Social security number'),
        ),
    ),
    StringField(
        name='bankNumber',
        widget=StringWidget(
            label=_(u'label_bankNumber', default=u'Bank number'),
        ),
    ),
    DateTimeField(
        name='workStartDate',
        validators=("isDateBeforeToday"),
    ),

    ImageField(
        name='portrait',
        widget=ImageWidget(
            label= PMF(u'label_portrait', default=u'Portrait'),
            ),
        original_size=(128, 128),
        ),

    ComputedField(
        searchable=True,
        name='title',
        widget=ComputedField._properties['widget'](
            label=_(u'plonehrm_label_title', default=u'Title'),
        ),
        accessor="Title"
    ),
),
)

Employee_schema = BaseFolderSchema.copy() + schema.copy()
Employee_schema.moveField('description', after='initials')
Employee_schema['title'].widget.visible = 0
Employee_schema['state'].widget.condition = 'object/showState'
Employee_schema['country'].widget.condition = 'object/showCountry'
Employee_schema['workStartDate'].widget.visible = {'edit': 'hidden',
                                                   'view': 'invisible'}

for schema_key in Employee_schema.keys():
    if not Employee_schema[schema_key].schemata == 'default':
        Employee_schema[schema_key].widget.visible={'edit':'invisible',
                                                    'view':'invisible'}


class Employee(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseFolder.__implements__, )
    implements(IEmployee, INonStructuralFolder)

    _at_rename_after_creation = True
    schema = Employee_schema

    security.declarePublic('Title')
    def Title(self):
        """Return title, composed of the first/middle/last names.
        """
        parts = [self.getFirstName(),
                 self.getMiddleName(),
                 self.getLastName()]
        # Filter out the empty bits:
        parts = [safe_unicode(part) for part in parts if part]
        return u' '.join(parts)

    security.declarePublic('getInitials')
    def getInitials(self):
        """Get the initials and possibly add dots
        """
        try:
            initials = self.initials
        except AttributeError:
            # Sometimes officialName gets called (to be catalogued)
            # before the initials attribute exists.
            return u''
        if initials and initials.find('.') == -1:
            # Add dots here
            initials = '.'.join(initials) + '.'
        return initials

    security.declarePublic('officialName')
    def officialName(self):
        """
        """
        parts = [self.getInitials(),
                 self.getMiddleName(),
                 self.getLastName()]
        # Filter out the empty bits:
        parts = [safe_unicode(part) for part in parts if part]
        return u' '.join(parts)

    security.declarePublic('hasPortrait')
    @property
    def hasPortrait(self):
        """ Checks if a portrait has been set for this employee.
        """
        return bool(self.getPortrait())

    security.declarePublic('showState')
    def showState(self):
        """Should the state widget be shown?
        """
        return self._extractVocabulary(name='show_state',
                                       default=True)

    security.declarePublic('showCountry')
    def showCountry(self):
        """Should the country widget be shown?
        """
        return self._extractVocabulary(name='show_country',
                                       default=True)

    security.declarePublic('_genderVocabulary')
    def _genderVocabulary(self):
        """Return vocabulary for gender.

        Well, they are titles really.
        """
        return DisplayList([
                ('female', _('label_madam', u'Madam')),
                ('male', _('label_sir', u'Sir')),
            ])

    security.declarePublic('_civilStatusVocabulary')
    def _civilStatusVocabulary(self):
        """Return vocabulary for civil status.
        """
        return self._extractVocabulary(name='civil_status_vocabulary',
                                       default=[])

    security.declarePublic('_idTypeVocabulary')
    def _idTypeVocabulary(self):
        """Return vocabulary for ID type.
        """
        return self._extractVocabulary(name='id_type_vocabulary',
                                       default=[])

    def _extractVocabulary(self, name='', default=True):
        """Return vocabulary by name.
        """
        pp = getToolByName(self, 'portal_properties')
        pdp = getattr(pp, 'personaldata_properties', None)
        if not pdp:
            return default
        return pdp.getProperty(name, default)

    def _getEndEmployeeAnnotations(self):
        """ Returns the Annotations linked to the employee.
        If they do not exists, it created them.
        """
        anno_key = 'plonehrm.employee'
        
        portal = getToolByName(self, 'portal_url').getPortalObject()
        annotations = IAnnotations(self)
        
        metadata = annotations.get(anno_key, None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

            metadata['endEmployment'] = PersistentDict()

        return metadata

    security.declarePublic('getEndEmploymentDate')
    def getEndEmploymentDate(self):
        """ Returns the date when the employee stopped woking for the
        company.
        """

        anno = self._getEndEmployeeAnnotations()
        if not 'endEmploymentDate' in anno:
            return None

        return anno['endEmploymentDate']

    security.declarePublic('setEndEmploymentDate')
    def setEndEmploymentDate(self, date):
        anno = self._getEndEmployeeAnnotations()
        anno['endEmploymentDate'] = date

        # We copy the default end employment checklist items.
        try:
            portal_checklist = self.portal_checklist
        except:
            # Should not happen.
            return

        try:
            checklist = self.checklist
        except:
            # Should not happen.
            return

        for item in portal_checklist.getEndContractItems():
            checklist.addItem(item.text)
       
    security.declarePublic('getEndEmploymentReason')
    def getEndEmploymentReason(self):
        """ Returns the reason why the employee stopped woking for the
        company.
        """

        anno = self._getEndEmployeeAnnotations()
        if not 'endEmploymentReason' in anno:
            return None

        return anno['endEmploymentReason']

    security.declarePublic('setEndEmploymentReason')
    def setEndEmploymentReason(self, reason):
        anno = self._getEndEmployeeAnnotations()
        anno['endEmploymentReason'] = reason


    def get_worked_days(self, start_date, end_date):
        """ Provides a dictionnary of boolean to know if
        a day was worked or not for the given period.
        The keys of the dictionnary are the dates between
        start_date and end_date.

        Only works for Arbo managers, as we use the way days
        are spread in a contract to compute the dictionnary.
        """
        def date_key(item):
            return item.getStartdate()

        def date_caster(day):
            """ Casts a DateTime object to datetime.date
            """
            return date(day.year(), day.month(), day.day())

        # We cast potential datetime to simple dates.
        try:
            start_date = start_date.date()
        except:
            pass

        try:
            end_date = end_date.date()
        except:
            pass

        worked_days = {}
        for i in range(0, end_date.toordinal() - start_date.toordinal() + 1):
            worked_days[start_date + timedelta(i)] = False

        
        contracts = self.contentValues({'portal_type': 'Contract'})
        letters = self.contentValues({'portal_type': 'Letter'})

        contracts = sorted(contracts, key = date_key)

        for contract in contracts:
            try:
                contract_end_date = date_caster(contract.expiry_date())
                contract_start_date = date_caster(contract.getStartdate())
            except:
                # One of the date has not been set, the contract can not
                # be used to compute worked days.
                continue

            # Check if the contract covers the period we want.
            if contract_end_date.toordinal() < start_date.toordinal() or \
               contract_start_date.toordinal() > end_date.toordinal():
                continue

            # We get the sub-period covered by this contract.
            if contract_start_date.toordinal() < start_date.toordinal():
                begin = start_date
            else:
                begin = contract_start_date

            if contract_end_date.toordinal() > end_date.toordinal():
                end = end_date
            else:
                end = contract_end_date

            end += timedelta(1)

            # We get the letters applicable during the contract.
            applicable_letters = [letter for letter in letters \
                                  if letter.getStartdate() > \
                                  contract.getStartdate() and \
                                  letter.getStartdate() < \
                                  contract.expiry_date()]

            # We sort the letter by start date.
            applicable_letters = sorted(applicable_letters,
                                        key = date_key)

            # Now, we look for each day from begin to end and will
            # mark it as worked or not.
            for i in range(0, end.toordinal() - begin.toordinal()):
                day = begin + timedelta(i)
                if not day in worked_days:
                    # Should not happen.
                    continue

                letter = None
                # We look if a letter covers this period.
                for j in reversed(range(0, len(applicable_letters))):
                    if date_caster(applicable_letters[j].getStartdate()).toordinal() <=\
                           day.toordinal():
                        letter = applicable_letters[j]
                        break

                # We get the way hours were spread.
                hour_spread = None
                if letter:
                    hour_spread = letter.hour_spread
                else:
                    hour_spread = contract.hour_spread

                # We get the information used to know if this
                # day was worked.
                day_number = day.weekday()
                week_number = day.isocalendar()[1]
                if week_number % 2:
                    week_type = 'odd'
                else:
                    week_type = 'even'

                # We update the 'worked_days' dictionnary.
                key = week_type + '_' + str(day_number)
                if key in hour_spread.hours:
                    worked_days[day] = hour_spread.hours[key] > 0
                else:
                    worked_days[day] = False

        return worked_days

    def get_last_contract(self):
        """ Fetches the last contract (or letter) of the
        employee (last in the meaning 'The one that ends the later'
        not 'The last one created'.)
        """
        contentFilter = {'portal_type': ['Contract', 'Letter']}
        brains = self.getFolderContents(contentFilter=contentFilter)
        if not brains:
            return None

        lastContract = brains[0].getObject()
        for brain in brains:
            contract = brain.getObject()

            if contract.expiry_date() > lastContract.expiry_date():
                lastContract = contract

        return lastContract


registerType(Employee, config.PROJECTNAME)
