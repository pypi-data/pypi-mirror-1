from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet
from zope.component import getAdapters


class EmployeeDetails(object):

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        self.__updated = True

        # Find all content providers for the region
        viewlets = getAdapters(
            (self.context, self.request, self.__parent__, self),
            IViewlet)

        viewlets = self.filter(viewlets)
        viewlets = self.sort(viewlets)

        # Just use the viewlets from now on
        self.viewlets = [viewlet for name, viewlet in viewlets]

        # Update all viewlets
        [viewlet.update() for viewlet in self.viewlets]

        self.columns = ([], [])
        left_column = True

        for viewlet in self.viewlets:
            if left_column:
                self.columns[0].append(viewlet)
            else:
                self.columns[1].append(viewlet)
            left_column = not left_column

    def sort(self, viewlets):
        columns = ()
        portal_props = getToolByName(self.context, 'portal_properties', None)
        if portal_props is not None:
            hrm_props = getattr(portal_props, 'plonehrm_properties', None)
            if hrm_props is not None:
                columns = hrm_props.getProperty('EmployeeDetailsViewlets', ())

        results = []
        for item in columns:
            for name, viewlet in viewlets:
                if name == item:
                    results.append((name, viewlet))
        return results


class EmployeesOverview(Explicit):
    index = ZopeTwoPageTemplateFile('employees.pt')
    worklocationview_attribute = 'active_employees'
    hrm_viewlet_property = 'EmployeesOverviewViewlets'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        columns = ()
        portal_props = getToolByName(self.context, 'portal_properties', None)
        if portal_props is not None:
            hrm_props = getattr(portal_props, 'plonehrm_properties', None)
            if hrm_props is not None:
                columns = hrm_props.getProperty(self.hrm_viewlet_property, ())
        rows = []
        view = self.context.restrictedTraverse('@@worklocationview')
        for brain in getattr(view, self.worklocationview_attribute):
            value = brain.getObject()
            rows.append(
                [getMultiAdapter(
                    (value, self.request, self.__parent__, self),
                    IViewlet, name=colname)
                 for colname in columns])
            [entry.update() for entry in rows[-1]]
        self.rows = rows

    def render(self, *args, **kw):
        return self.index(*args, **kw)


class InactiveEmployeesOverview(EmployeesOverview):
    index = ZopeTwoPageTemplateFile('employees.pt')
    worklocationview_attribute = 'inactive_employees'


class EmployeesImprovementsOverview(EmployeesOverview):
    hrm_viewlet_property = 'EmployeesImprovementsOverviewViewlets'
