from zope.interface import implements
from plone.app.contentmenu.menu import WorkflowMenu
from plone.app.contentmenu.interfaces import IWorkflowMenu

class PloneHrmWorkflowMenu(WorkflowMenu):
    """ Overrides the Plone default class to display workflow menus in
    order to hide them in the absence view.
    """
    implements(IWorkflowMenu)

    def getMenuItems(self, context, request):
        if context.getPortalTypeName() in ['Absence', 'Employee']:
            return []
        else:
            return WorkflowMenu.getMenuItems(self, context, request)
