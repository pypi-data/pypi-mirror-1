__author__ = """Reinout van Rees <reinout@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('plonehrm')
logger.debug('Installing Product')

from zope.i18nmessageid import MessageFactory
PloneHrmMessageFactory = MessageFactory(u'plonehrm')

from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory

from Products.plonehrm import config
from Products.validation import validation
from validator import DateValidator, AgeValidator, BSNValidator
validation.register(DateValidator('isDateBeforeToday'))
validation.register(AgeValidator('checkIfTooYoung'))
validation.register(BSNValidator('isBSNValid'))
registerDirectory('skins', config.product_globals)

def initialize(context):
    # imports packages and types for registration
    import content

    permissions = dict(WorkLocation='plonehrm: Add worklocation',
                       Employee='plonehrm: Add employee',
                       Template='plonehrm: Add template')

    # Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types = (atype, ),
            permission = permissions[atype.portal_type],
            extra_constructors = (constructor, ),
            ).initialize(context)
