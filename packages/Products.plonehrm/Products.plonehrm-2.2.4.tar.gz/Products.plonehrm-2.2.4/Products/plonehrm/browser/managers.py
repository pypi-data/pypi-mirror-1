from datetime import date
from datetime import timedelta
import logging

from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet
from zope.component import getAdapters

logger = logging.getLogger('Products.plonehrm')


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
            try:
                value = brain.getObject()
            except (AttributeError, KeyError):
                logger.warn("Error getting object at %s", brain.getURL())
                continue
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


class EmployeesAbsenceOverview(EmployeesOverview):
    hrm_viewlet_property = 'EmployeesAbsenceViewlets'
    index = ZopeTwoPageTemplateFile('absences.pt')

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        today = date.today()
        year = today.year
        columns = ()
        portal_props = getToolByName(self.context, 'portal_properties', None)
        if portal_props is not None:
            hrm_props = getattr(portal_props, 'plonehrm_properties', None)
            if hrm_props is not None:
                columns = hrm_props.getProperty(self.hrm_viewlet_property, ())
        rows = []
        view = self.context.restrictedTraverse('@@worklocationview')
        for brain in getattr(view, self.worklocationview_attribute):
            employee = brain.getObject()
            cols = []
            fullname = getMultiAdapter(
                (employee, self.request, self.__parent__, self),
                IViewlet, name='plonehrm.fullname')
            fullname.update()
            cols.append(fullname.render())
            # Now calculate absence days.
            months = {}
            for month in range(1, 13):
                months[month] = 0
            absences = employee.contentValues({'portal_type': 'Absence'})
            this_day = date(year, 1, 1) # 1 January of this year
            days_handled = 0 # We use this as safety against never-ending loops
            for absence in absences:
                if absence.end_date and absence.end_date.year < today.year:
                    # irrelevant
                    continue
                if absence.start_date.year > today.year:
                    # This and all next absences start in the future.
                    break
                # We have found a relevant absence.
                if absence.end_date:
                    end_date = absence.end_date.date()
                else:
                    end_date = today
                start_date = absence.start_date.date()
                days_absent = absence.days_absent()
                full_duration = end_date - start_date
                if full_duration.days == 0:
                    # Avoid ZeroDivisionError
                    full_duration = days_absent or 1
                else:
                    full_duration = full_duration.days
                if days_absent > full_duration:
                    # A bit weird.  Possibly we are looking at an
                    # earlier year (which is not supported yet in the
                    # UI, but can happen when you are setting 'today'
                    # to something else when testing/hacking).
                    days_absent = full_duration

                # What percentage are we adding per day?
                per_day = days_absent / float(full_duration)

                # Find the next absence.
                while start_date > this_day and days_handled <= 366:
                    days_handled += 1
                    this_day += timedelta(1)
                if days_handled > 366:
                    # No relevant dates anymore
                    break

                # Add the 'per_day' amount to the current month until
                # we find the end_date of the current absence.
                while end_date >= this_day and days_handled <= 366:
                    months[this_day.month] += per_day
                    days_handled += 1
                    this_day += timedelta(1)
                if days_handled > 366:
                    # No relevant dates anymore
                    break

            total = 0
            for month in range(1, 13):
                value = int(round(months[month]))
                total += value
                cols.append(value)
            cols.append(total)

            rows.append(cols)
        self.rows = rows

    def render(self, *args, **kw):
        return self.index(*args, **kw)
