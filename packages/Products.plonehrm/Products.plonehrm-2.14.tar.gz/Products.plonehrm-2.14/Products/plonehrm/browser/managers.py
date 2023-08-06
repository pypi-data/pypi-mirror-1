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

        self.average_percentage = 0
        self.average_total = 0
        self.average_count = 0

    def get_employee_absences_number(self, employee):
        """ Gets every absences of an employee for this year.
        """
        year = date.today().year
        total = 0

        absences = employee.contentValues({'portal_type': 'Absence'})

        return len([absence for absence in absences
                    if absence.start_date.year == year])

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

    def absence_percentage(self, employee):
        """ Provides percentage of days missed for the current year.
        """
        def date_key(item):
            return item.getStartdate()

        today = DateTime()
        year_begin = DateTime(today.year(), 1, 1)

        # We get employee contracts and letters
        contracts = employee.contentValues({'portal_type': 'Contract'})
        letters = employee.contentValues({'portal_type': 'Letter'})

        # Number of days worked from first of january to now.
        worked_days = 0

        # Date from which we start counting worked days (basically, 1st
        # of january or first contract start date).
        # We initialize it to today and adjust its value when looking
        # at the contracts.
        period_begin_date = today

        # True if the first of january covered by a contract.
        is_first_of_january_covered = False

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

            # We look if this contract covers the 1st of january.
            if year_begin > contract.getStartdate() and \
               year_begin < contract.expiry_date():
                is_first_of_january_covered = True
                period_begin_date = year_begin

            # If no contract covers the 1st a january, we set the value of
            # period_begin_date to the first contract found.
            if not is_first_of_january_covered and \
               contract.getStartdate() < period_begin_date:
                period_begin_date = contract.getStartdate()

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

        # We compute the sickdays. We can not use the one computed for the total
        # as this total takes into account all absences for the year, we just
        # need absences for the period covered by contracts.
        # We also need to cast period_begin_date form DateTime to date.
        period_begin_date = date(period_begin_date.year(),
                                 period_begin_date.month(),
                                 period_begin_date.day())

        sickdays = self.get_employee_absences(employee, as_list=False,
                                              startdate = period_begin_date)

        if worked_days:
            # We finally compare number of sickdays and number of worked days.
            absence_percentage = int((sickdays / worked_days) * 100)

            # There is some weird cases where we get more than 100% of absences
            # over the year, for example when the first contract is signed
            # during an absence.
            # To prevent this, we return 100%.
            if absence_percentage > 100:
                return 100
            else:
                return absence_percentage

    def get_arbo_absence(self, employee):
        """ This method computes number of absence days each month,
        and the percentage of missed day for the whole year.
        Contrary to the previous methods, it does not take into account
        number of absence days specified in the absence, but the beginning
        and ending of an absence and compares is to how days are spread
        during a week.

        To do this, we will compute two dictionnaries. The key will be the
        dates and the value floats.
        The first dictionnary tells if the day was worked, the second one if
        the employee was present (and how much if the absence did not start
        in the morning).
        """

        def date_key(item):
            return item.getStartdate()

        def date_caster(day):
            """ Casts a DateTime object to datetime.date
            """
            return date(day.year(), day.month(), day.day())

        # Some important dates
        today = date.today()
        year = today.year
        first_day = date(year, 1, 1)

        # The dictionnaries of worked/absence days.
        worked_days = {}
        absence_days = {}

        for i in range(0, today.toordinal() - first_day.toordinal() + 1):
            worked_days[first_day + timedelta(i)] = 0
            absence_days[first_day + timedelta(i)] = 0

        # Number of not-worked days per month
        months = {}
        for month in range(1, 13):
            months[month] = 0

        # Count of absences for this year.
        absence_count = 0

        # Total of absence days.
        absence_days_total = 0

        # Total of worked days.
        worked_days_total = 0

        # We get employee absences.
        absences = employee.contentValues({'portal_type': 'Absence'})

        # First, we compute the absence days.
        for absence in absences:
            if absence.end_date and not absence.end_date.year == year:
                # This absence is not in the range of interresting absences.
                continue

            absence_count += 1

            # We compute the days that was supposed to be worked during
            # the absence.
            if absence.end_date:
                days = employee.get_worked_days(absence.start_date,
                                                absence.end_date)
            else:
                days = employee.get_worked_days(absence.start_date,
                                                today)

            for day in days:
                if days[day]:
                    absence_days[day] = 1
                else:
                    absence_days[day] = 0

            # We update the first cell of the dictionnary for
            # absence starting on a partial day.
            casted_start_date = date(absence.start_date.year,
                                     absence.start_date.month,
                                     absence.start_date.day)

            if casted_start_date in absence_days:
                absence_days[casted_start_date] = \
                            absence.get_first_day_percentage()

        # Now we compute which days were supposed to be worked.
        worked_days = employee.get_worked_days(first_day, today)

        # Now, we can compute for each day if the employee
        # worked or was absent.
        # We substract absence days to worked days to know how long
        # the employee worked this day.
        for day in worked_days:
            if day.toordinal() > today.toordinal() or \
               not day in absence_days:
                continue

            if worked_days[day]:
                worked_days_total += 1
                worked_time = 1 - absence_days[day]

                if worked_time != 1:
                    absence_days_total += absence_days[day]

                    if day.month in months:
                        months[day.month] += absence_days[day]

        # Now we can create the row that will be displayed.

        # First, we add the name of the employee.
        fullname = getMultiAdapter(
            (employee, self.request, self.__parent__, self),
            IViewlet, name='plonehrm.fullname')
        fullname.update()

        result = [fullname.render()]

        # Then, one cell for each month.
        for month in months:
            value = months[month]
            result.append(value)

        # Then, the total of absence days.
        result.append(absence_days_total)

        # Then, the percentage of absences.
        if worked_days_total:
            result.append(str(int(
                (float(absence_days_total)/worked_days_total) * 100)) + '%')
        else:
            result.append('0%')

        # And to finish, the count of absences.
        result.append(absence_count)
        return result

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

        # We check if the user has the ARBO manager role.
        membership = getToolByName(self.context, 'portal_membership')
        is_arbo = membership.checkPermission('plonehrm: manage Arbo content',
                                             self.context)

        for brain in getattr(view, self.worklocationview_attribute):
            employee = brain.getObject()

            # For Arbo manager, we use a special method to compute rows.
            if is_arbo:
                rows.append(self.get_arbo_absence(employee))
                continue

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
            percentage = self.absence_percentage(employee)
            if percentage:
                percentage = str(percentage) + '%'
            else:
                percentage = '0%'
            cols.append(percentage)

            # And now the total of absences
            cols.append(self.get_employee_absences_number(employee))

            rows.append(cols)
        self.rows = rows

        # Now we compute the average percentage/total and count of absences.
        for row in self.rows:
            self.average_count += row[-1]
            self.average_total += row[-3]
            try:
                # We have to remove last character in percentage row and cast it
                # to an integer.
                self.average_percentage += int(row[-2][:-1])
            except ValueError:
                pass

        if self.rows:
            self.average_count /= len(self.rows)
            self.average_percentage /= len(self.rows)
            self.average_total /= len(self.rows)
        else:
            self.average_count = 0
            self.average_percentage = 0
            self.average_total = 0

        self.average_percentage = str(self.average_percentage) + '%'

    def render(self, *args, **kw):
        return self.index(*args, **kw)
