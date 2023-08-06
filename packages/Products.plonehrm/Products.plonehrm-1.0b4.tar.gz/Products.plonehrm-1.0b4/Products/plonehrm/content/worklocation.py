__author__ = """Reinout van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import registerType
from zope.interface import implements

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm import config
from Products.plonehrm.interfaces import IWorkLocation

schema = Schema((
    StringField(
        name='officialName',
        widget=StringWidget(
            label=_(u'plonehrm_label_officialName', default=u'Legal company name'),
        ),
    ),
    LinesField(
        name='address',
        widget=LinesField._properties['widget'](
            label=_(u'plonehrm_label_address', default=u'Address'),
        ),
    ),
    StringField(
        name='postalCode',
        widget=StringWidget(
            label=_(u'plonehrm_label_postalCode', default=u'Zip code'),
        )
    ),
    StringField(
        name='city',
        widget=StringWidget(
            label=_(u'plonehrm_label_city', default=u'City'),
        )
    ),
    StringField(
        name='telephone',
        widget=StringWidget(
            label=_(u'plonehrm_label_telephone', default=u'Phone number'),
        ),
    ),
),
)

WorkLocation_schema = ATFolderSchema.copy() + schema.copy()


class WorkLocation(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),)
    implements(IWorkLocation)

    _at_rename_after_creation = True
    schema = WorkLocation_schema

registerType(WorkLocation, config.PROJECTNAME)
