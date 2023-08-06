__author__ = """Reinout van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

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
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.utils import safe_unicode
from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm import config
from Products.plonehrm.interfaces import IEmployee
from zope.interface import implements


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
        required=1,
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
        widget=CalendarWidget(
            starting_year=1940,
            show_hm=0,
            label=_(u'label_work_start_date', default=u'Work start date'),
        ),
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
        initials = self.initials
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
        return DisplayList([
                ('married', _('label_married', u'married')),
                ('notmarried', _('label_not_married', u'not married')),
            ])

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


registerType(Employee, config.PROJECTNAME)
