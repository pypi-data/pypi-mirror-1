import logging

from Products.CMFCore.utils import getToolByName

from Products.plonehrm import utils


logger = logging.getLogger("plonehrm")


def update_worklocations(context):
    """Make sure all work locations have all the plonehrm placeful workflow.
    """
    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(portal_type='WorkLocation'):
        worklocation = brain.getObject()
        utils.set_plonehrm_workflow_policy(worklocation)
    logger.info('Set the plonehrm workflow policy in all work locations.')
    workflow = getToolByName(context, 'portal_workflow')
    workflow.updateRoleMappings()
    logger.info('Updated the role mappings in the site.')
