__author__ = """Reinout van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import BaseFolderSchema


from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import registerType
from zope.interface import implements

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm import config
from Products.plonehrm.interfaces import IWorkLocation

schema = Schema((
    StringField(
        name='address',
        widget=StringWidget(
            label=_(u'plonehrm_label_address',
                    default=u'Work Location Address'),
            description=_(
                    u'plonehrm_help_address',
                    default=u'Visiting address of the actual work location'),
        ),
    ),
    StringField(
        name='postalCode',
        widget=StringWidget(
            label=_(u'plonehrm_label_postalCode',
                    default=u'Work Location Zip Code'),
        ),
    ),
    StringField(
        name='city',
        widget=StringWidget(
            label=_(u'plonehrm_label_city',
                    default=u'Work Location City'),
        ),
    ),
    StringField(
        name='contactPerson',
        widget=StringWidget(
            label=_(u'plonehrm_label_contactperson',
                    default=u'Contact person'),
        ),
    ),

    StringField(
        name='telephone',
        widget=StringWidget(
            label=_(u'plonehrm_label_telephone', default=u'Phone number'),
        ),
    ),
    StringField(
        name='officialName',
        widget=StringWidget(
            label=_(u'plonehrm_label_officialName',
                    default=u'Legal company name'),
        ),
    ),
    StringField(
        name='companyAddress',
        widget=StringWidget(
            label=_(u'plonehrm_label_companyAddress',
                    default=u'Company Address'),
            description=_(u'plonehrm_help_companyAddress',
                          default=u'Postal address of the main office'),
        ),
    ),
    StringField(
        name='companyPostalCode',
        widget=StringWidget(
            label=_(u'plonehrm_label_companyPostalCode',
                    default=u'Company Zip Code'),
        ),
    ),
    StringField(
        name='companyCity',
        widget=StringWidget(
            label=_(u'plonehrm_label_companyCity',
                    default=u'Company City'),
        ),
    ),
    IntegerField(
        name='vacationDays',
        widget=IntegerWidget(
            label=_(u'plonehrm_label_vacationDays', default=u'Vacation days'),
            description=_(u'plonehrm_help_vacationDays',
                          default=u'Number of vacation days per year'),
        ),
    ),
    StringField(
        name='payPeriod',
        widget=SelectionWidget(
            label=_(u'label_pay_period', default=u'Pay period'),
        ),
        vocabulary='_payPeriodVocabulary',
    ),
    StringField(
        name='insuranceName',
        widget=StringWidget(
            label=_(u'label_insurance_name', default=u'Company name'),
        ),
        schemata = 'insurance',
    ),
    StringField(
        name='insuranceNumber',
        widget=StringWidget(
            label=_(u'label_insurance_number', default=u'Insurance number'),
        ),
        schemata = 'insurance',
    ),
    StringField(
        name='insuranceContact',
        widget=StringWidget(
            label=_(u'label_insurance_contact', default=u'Contact name'),
        ),
        schemata = 'insurance',
    ),
    StringField(
        name='insuranceAddress',
        widget=StringWidget(
            label=_(u'label_insurance_address', default=u'Address'),
        ),
        schemata = 'insurance',
    ),
    StringField(
        name='insuranceZipCode',
        widget=StringWidget(
            label=_(u'label_insurance_zipcode', default=u'Zip code'),
        ),
        schemata = 'insurance',
    ),
    StringField(
        name='insuranceCity',
        widget=StringWidget(
            label=_(u'label_insurance_city', default=u'City'),
        ),
        schemata = 'insurance',
    ),
    StringField(
        name='insurancePhone',
        widget=StringWidget(
            label=_(u'label_insurance_phone', default=u'Phone'),
        ),
        schemata = 'insurance',
    ),
    ),
)

WorkLocation_schema = BaseFolderSchema.copy() + schema.copy()
WorkLocation_schema['title'].widget.label = _(
    u'plonehrm_label_trade_name', default=u'Trade Name')
# Move description field out of the way:
WorkLocation_schema['description'].schemata = 'categorization'

for schema_key in WorkLocation_schema.keys():
    if WorkLocation_schema[schema_key].schemata in ['metadata',
						    'categorization']:
	WorkLocation_schema[schema_key].widget.visible={'edit':'invisible',
							'view':'invisible'}

class WorkLocation(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder, '__implements__', ()), )
    implements(IWorkLocation)

    _at_rename_after_creation = True
    schema = WorkLocation_schema

    security.declarePublic('_payPeriodVocabulary')
    def _payPeriodVocabulary(self):
        """Return vocabulary for payPeriod.

        Well, they are titles really.
        """
        return DisplayList([
                ('month', _('label_pay_period_month', u'month')),
                ('4weeks', _('label_pay_period_four_weeks', u'4 weeks')),
                ('1week', _('label_pay_period_one_week', u'1 week')),
            ])


registerType(WorkLocation, config.PROJECTNAME)
