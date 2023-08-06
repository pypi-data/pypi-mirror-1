from datetime import date
from datetime import timedelta
from DateTime import DateTime
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

    def get_employee_absences(self, employee, as_list=True, startdate = None):
        """ Computes the number of days an employee was absent
        for the current year.
        If as_list is set to True, a list of absences for each month
        is returned, else the total for the year is returned.
        """
        today = date.today()
        year = today.year
        
        months = {}
        total = 0
        
        for month in range(1, 13):
            months[month] = 0
        absences = employee.contentValues({'portal_type': 'Absence'})

        if startdate is None:
            this_day = date(year, 1, 1) # 1 January of this year
        else:
            this_day = startdate
            
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

        for month in range(1, 13):
            total += months[month]

        if as_list:
            return months
        else:
            return total

    def absence_percentage(self, employee, sickdays):
        """ Provides percentage of days missed for the current year.
        """
        def date_key(item):
            return item.getStartdate()

        today = DateTime()
        year_begin = DateTime(today.year(), 1, 1)

        # We get employee contracts and letters
        contracts = employee.contentValues({'portal_type': 'Contract'})
        letters = employee.contentValues({'portal_type': 'Letter'})

        worked_days = 0
        period_begin_date = None

        contracts = sorted(contracts, key=date_key)
        for contract in contracts:
            # We look if the contract covers the period between
            # 1st january and today.
            if contract.expiry_date() < year_begin or \
               contract.getStartdate() > today:
                continue

            # We get the number of days covered by this contract
            begin = max([contract.getStartdate(), year_begin])
            end = min([contract.expiry_date(), today])

            # If this is the first contract treated, we keep the begin date
            # to compute absences days.
            if contract == contracts[0]:
                period_begin_date = date(begin.year(),
                                         begin.month(),
                                         begin.day())

            # We get the letters covering his period
            applicable_letters = [letter for letter in letters \
                                  if letter.getStartdate() > begin and \
                                  letter.getStartdate() < end]

            if not applicable_letters:
                # We compute the number of days that were supposed to be worked
                # during this period
                contract_days = end - begin
                worked_days += contract_days * (contract.getDaysPerWeek() / 7.0)

            else:
                # In this case, we have to split the contract period
                # to get every changes due to letters.
                applicable_letters = sorted(applicable_letters,
                                            key = date_key)

                # We compute days covered by the basic contract.
                end = applicable_letters[0].getStartdate()
                contract_days = end - begin
                worked_days += contract_days * (contract.getDaysPerWeek() / 7.0)

                i = 1
                for letter in applicable_letters:
                    # We compute days covered by each letter.
                    if i == len(applicable_letters):
                        end = min([contract.expiry_date(), today])
                    else:
                        end = min([applicable_letters[i].getStartdate(), today])

                    begin = letter.getStartdate()
                    i += 1
                    
                    letter_days = end - begin
                    worked_days += letter_days * (letter.getDaysPerWeek() / 7.0)

        if worked_days:
            # We finally compare number of sickdays and number of worked days.
            return int((sickdays / worked_days) * 100)    

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
            months = self.get_employee_absences(employee)

            total = 0
            for month in range(1, 13):
                value = int(round(months[month]))
                total += value
                cols.append(value)
            cols.append(total)

            # Now computes the percentage of absences.
            percentage = self.absence_percentage(employee, total)
            if percentage:
                percentage = str(percentage) + '%'
            else:
                percentage = '0%'
            cols.append(percentage)

            rows.append(cols)
        self.rows = rows

    def render(self, *args, **kw):
        return self.index(*args, **kw)
