from datetime import date
from datetime import timedelta

from Products.Five import BrowserView

class EmployeeAbsences(BrowserView):
    """ This class is not a real view, but is used to manage
    some code shared between views of worklocation and absences.
    """

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
