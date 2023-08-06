__author__ = """Reinout van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import ComputedField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import registerType
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm import config
from Products.plonehrm.interfaces import IEmployee


schema = Schema((
    StringField(
        name='firstName',
        widget=StringWidget(
            label=_(u'plonehrm_label_firstName', default=u'Firstname'),
        )
    ),
    StringField(
        name='middleName',
        widget=StringWidget(
            label=_(u'plonehrm_label_middleName', default=u'Middle name'),
        )
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


class Employee(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseFolder.__implements__,)
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

registerType(Employee, config.PROJECTNAME)
