import cStringIO

from Acquisition import Explicit
from zope.i18n import translate
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.Five import BrowserView
from datetime import date
from Acquisition import aq_chain, aq_parent
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate

try:
    from plonehrm.absence.absence import IAbsenceAdapter
except ImportError:
    IAbsenceAdapter = None

from Products.plonehrm import PloneHrmMessageFactory as _
from plonehrm.absence import AbsenceMessageFactory as _a
from Products.CMFPlone import PloneMessageFactory as _p
from unicode_csv import UnicodeDictWriter

class AbsenceView(Explicit):
    """Return the number of sick days of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Number of sickdays'

    def render(self):
        if self.is_sick():
            days = self.days_absent()
        return [days, days]

class AbsenceExportView(BrowserView):
    """ Produces a CSV file.
    """
    def _fieldnames(self):
        return ['employee',
                'sofi',
                'reason',
                'isaccident',
                'startdate',
                'enddate',
                'lenght']

    def get_lang(self):
        props = getToolByName(self.context, 'portal_properties')
        return props.site_properties.getProperty('default_language')
    
    def _header(self):
        """ Returns a dictionnary describing columns of the CSV export.
        """
        lang = self.get_lang()
        
        header = {}
        header['employee'] = translate(_p(u'Employee'),
                                       target_language=lang,
                                       context=self.request)

        header['sofi'] = translate(_(u'label_socialSecurityNumber'),
                                   target_language=lang)
        
        header['reason'] = translate(_a(u'heading_reason'),
                                     target_language=lang)

        header['isaccident'] = translate(_a(u'heading_accident'),
                                          target_language=lang)

        header['startdate'] = translate(_a(u'label_start_date'),
                                         target_language=lang)

        header['enddate'] = translate(_a(u'label_end_date'),
                                       target_language=lang)

        header['lenght'] = translate(_a(u'label_days_absent'),
                                     target_language=lang)

        return header

    def absence_to_row(self, absence, is_arbo, start_date, end_date):
        """ Produces a dictionnary form an absence. This dictionnary can
        be used as an input row for UnicodeDictWriter.
        """
        lang = self.get_lang()
        toLocalizedTime = self.context.restrictedTraverse('@@plone').toLocalizedTime
        employee = aq_parent(absence)
        row = {}

        row['employee'] = employee.officialName()
        row['sofi'] = employee.getSocialSecurityNumber()
        row['reason'] = absence.title

        if absence.is_accident:
            row['isaccident'] = translate(_p(u'Yes', default=u'Yes'),
                                          target_language=lang,
                                          context=self.request)
        else:
            row['isaccident'] = translate(_p(u'No', default=u'No'),
                                          target_language=lang,                                          
                                          context=self.request)

        row['startdate'] = toLocalizedTime(absence.start_date.isoformat())
        if absence.end_date:
            row['enddate'] = toLocalizedTime(absence.end_date.isoformat())
        else:
            row['enddate'] = u''
            
        length = absence.days_absent(is_arbo, start_date, end_date)
        # Use comma instead of dots
        row['lenght'] = ','.join(str(length).split('.'))

        return row

    def filter_absences(self, start_date, end_date):
        """ Returns the list of absences covering the period
        between start_date and end_date.
        """
        absences = []

        employees = self.context.getFolderContents(
            contentFilter={'portal_type': 'Employee'})
        for emp in employees:
            emp = emp.getObject()
            emp_absences = emp.getFolderContents(
                contentFilter={'portal_type': 'Absence'})

            for absence in emp_absences:
                absence = absence.getObject()

                # We only chose absences for the covered period.
                if absence.end_date:
                    if not absence.end_date.toordinal() < \
                           start_date.toordinal() and \
                       not absence.start_date.toordinal() > \
                           end_date.toordinal():
                        absences.append(absence)
                else:
                    if not absence.start_date.toordinal() > \
                           end_date.toordinal():
                        absences.append(absence)

        return absences

    def check_form(self, form):
        """ Checks the submitted form and returns start and end date
        in a suitable format.
        
        """
        # We check that fields have been submitted.
        fields = ['export_end_date_day',
                  'export_end_date_month',
                  'export_end_date_year',
                  'export_start_date_day',
                  'export_start_date_month',
                  'export_start_date_year']

        for field in fields:
            if not field in form:
                # Should not hapen.
                return
       
        try:
            start_day = int(form['export_start_date_day'])
            start_month = int(form['export_start_date_month'])
            start_year = int(form['export_start_date_year'])
            start_date = date(start_year, start_month, start_day)
        except:
            start_date = date.today()

        try:
            end_day = int(form['export_end_date_day'])
            end_month = int(form['export_end_date_month'])
            end_year = int(form['export_end_date_year'])
            end_date = date(end_year, end_month, end_day)
        except:
            end_date = date.today()

        return start_date, end_date

    def __call__(self):
        form = self.request.form
        membership = getToolByName(self.context, 'portal_membership')
        is_arbo = membership.checkPermission('plonehrm: manage Arbo content',
                                             self.context)

        try:
            start_date, end_date = self.check_form(form)
        except:
            # Some fields were missing, should not happen.
            return

        # We get all absences
        absences = self.filter_absences(start_date, end_date)

        # Now we can make the CSV export.
        fileobj = cStringIO.StringIO()
        writer = UnicodeDictWriter(fileobj, self._fieldnames(),
                                   extrasaction='ignore', dialect='excel',
                                   delimiter=';')

        writer.writerow(self._header())
        
        for absence in absences:
            writer.writerow(self.absence_to_row(absence, is_arbo,
                                                start_date, end_date))
        
        fileobj.seek(0)
        filename='export-absences.csv'
        self.request.response.setHeader('Cache-Control',
                                        'no-store, no-cache, must-revalidate')
        self.request.response.setHeader('Content-Type',
                                        'text/comma-separated-values')
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename="%s"' % filename)
        self.request.response.write(fileobj.read())
