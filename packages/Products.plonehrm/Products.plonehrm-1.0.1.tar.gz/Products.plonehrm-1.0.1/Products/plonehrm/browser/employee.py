from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch
from Products.Five import BrowserView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet


class EmployeeView(BrowserView):
    @property
    def extraItems(self):
        all = self.context.getFolderContents()
        # Filter out the employee module items.
        moduleTypes = []
        portal_props = getToolByName(self.context,
                                     'portal_properties', None)
        if portal_props is not None:
            hrm_props = getattr(portal_props, 'plonehrm_properties', None)
            if hrm_props is not None:
                moduleTypes = hrm_props.getProperty(
                    'employee_module_portal_types', ())
        rest = [item for item in all
                 if item['portal_type'] not in moduleTypes]
        # Turn 'rest' into a batch for the benefit of the tabular folder
        # macro.
        b_start = 0
        b_size = 1000
        rest = Batch(rest, b_size, b_start, orphan=0)
        return rest


class FullnameView(Explicit):
    """Return the fullname of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Fullname'

    def render(self):
        return '<a href="%s">%s</a>' % (self.context.getId(),
                                        self.context.Title())
