from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.app.container.interfaces import INameChooser
from zope.component import getUtility, getMultiAdapter
from zope.interface import implements
import transaction

from Products.plonehrm import config
from Products.plonehrm import utils
from Products.plonehrm.browser import substitution as parameter_portlet


class HiddenProducts(object):
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return [
            u'plonehrm.jobperformance',
            u'plonehrm.checklist',
            u'plonehrm.contracts',
            u'plonehrm.personaldata',
            u'plonehrm.notes',
            u'plonehrm.absence',
            ]


def setup(context):
    # This is the main method that gets called by genericsetup.
    if context.readDataFile('plonehrm.txt') is None:
        return
    site = context.getSite()
    logger = context.getLogger('plonehrm')
    install_dependencies(site, logger)
    install_placeful_workflow(site, logger)
    update_employees(site, logger)
    unindex_tools(site, logger)
    install_parameter_portlet(site, logger)
    add_properties(site, logger)


def install_dependencies(site, logger):
    # Since plone 3.1, genericsetup handles dependencies, where we did it by
    # hand. I've decided to keep it that way as we're reinstalling everything
    # every time. [reinout]
    setup = getToolByName(site, 'portal_setup')
    qi = getToolByName(site, 'portal_quickinstaller')
    for product in config.QI_DEPS:
        if not qi.isProductInstalled(product):
            qi.installProduct(product, locked=True, hidden=True)
            transaction.savepoint(optimistic=True)
            logger.info("Installed %s.", product)
    # Now reinstall all products for good measure.
    qi.reinstallProducts(config.QI_DEPS)
    logger.info("Reinstalled %s.", config.QI_DEPS)


def install_placeful_workflow(site, logger):
    """Install our placeful workflow.

    We cannot guarantee that CMFPlacefulWorkflow is installed (with
    the install_dependencies method) *before* our portal_workflow.xml
    has been processed.  So we explicitly to process it (again)
    afterwards.
    """
    logger.info('Explicitly running our portal_placeful_workflow step.')
    setup = getToolByName(site, 'portal_setup')
    setup.runImportStepFromProfile('profile-Products.plonehrm:default',
                                   'placeful_workflow')


def unindex_tools(site, logger):
    # Tools that are added by dependencies unfortunately end up
    # visible in the folder_contents.  Should possibly be fixed in
    # GenericSetup/tool.py:importToolset().  Let's fix it here
    # temporarily afterwards for all tool ids that we expect.
    possible_ids = ['portal_contracts', 'portal_jobperformance',
                    'portal_checklist', 'portal_absence']
    for id_ in possible_ids:
        tool = getToolByName(site, id_, None)
        if tool is not None:
            tool.unindexObject()


def update_employees(site, logger):
    """Upon a reinstall, make sure all employees have all modules.
    """
    catalog = getToolByName(site, 'portal_catalog')
    for brain in catalog(portal_type='Employee'):
        try:
            employee = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue
        utils.updateEmployee(employee)
    logger.info('Updated the employees')


def install_parameter_portlet(site, logger):
    """Add parameter portlets to the right column in the tools.

    Note that we cannot do this with portlets.xml, as that doesn't handle
    assignments that are not in the portal root, apparently.
    """
    contracts = getToolByName(site, 'portal_contracts')
    jobperformance = getToolByName(site, 'portal_jobperformance')
    tools = (contracts, jobperformance)
    for tool in tools:
        column = getUtility(IPortletManager, name="plone.rightcolumn",
                            context=tool)
        manager = getMultiAdapter((tool, column), IPortletAssignmentMapping)
        portletnames = [v.title for v in manager.values()]
        chooser = INameChooser(manager)

        assignment = parameter_portlet.Assignment()
        title = assignment.title
        if title not in portletnames:
            manager[chooser.chooseName(title, assignment)] = assignment


def add_properties(site, logger):
    """Add properties to portal_properties.plonehrm_properties.

    We do that in python code instead of in propertiestool.xml to
    avoid overwriting changes by the user.

    Same for personaldata_properties.
    """
    portal_props = getToolByName(site, 'portal_properties')
    props = portal_props.plonehrm_properties
    for propname, propdata in config.PLONEHRM_PROPERTIES.items():
        if not props.hasProperty(propname):
            props._setProperty(propname, propdata['default'], propdata['type'])
            logger.info('Added property %r with default value %r',
                        propname, propdata['default'])

    props = portal_props.personaldata_properties
    for propname, propdata in config.PERSONALDATA_PROPERTIES.items():
        if not props.hasProperty(propname):
            props._setProperty(propname, propdata['default'], propdata['type'])
            logger.info('Added property %r with default value %r',
                        propname, propdata['default'])
