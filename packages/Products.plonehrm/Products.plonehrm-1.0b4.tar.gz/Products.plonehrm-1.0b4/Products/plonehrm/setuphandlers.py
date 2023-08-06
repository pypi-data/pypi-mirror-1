from Products.CMFCore.utils import getToolByName
from Products.plonehrm import config
from Products.plonehrm import utils
import transaction
from zope.interface import implements
from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from zope.app.container.interfaces import INameChooser
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
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
            ]


def setup(context):
    # This is the main method that gets called by genericsetup.
    if context.readDataFile('plonehrm.txt') is None:
        return
    site = context.getSite()
    logger = context.getLogger('plonehrm')
    install_dependencies(site, logger)
    update_employees(site, logger)
    unindex_tools(site, logger)
    install_parameter_portlet(site, logger)


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


def unindex_tools(site, logger):
    # Tools that are added by dependencies unfortunately end up
    # visible in the folder_contents.  Should possibly be fixed in
    # GenericSetup/tool.py:importToolset().  Let's fix it here
    # temporarily afterwards for all tool ids that we expect.
    possible_ids = ['portal_contracts', 'portal_jobperformance',
                    'portal_checklist']
    for id_ in possible_ids:
        tool = getToolByName(site, id_, None)
        if tool is not None:
            tool.unindexObject()


def update_employees(site, logger):
    """Upon a reinstall, make sure all employees have all modules.
    """
    catalog = getToolByName(site, 'portal_catalog')
    for brain in catalog(portal_type='Employee'):
        employee = brain.getObject()
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
