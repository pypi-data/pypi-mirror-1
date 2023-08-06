from DateTime import DateTime
from Acquisition import aq_inner, aq_parent, aq_chain
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch
from Products.Five import BrowserView
from plone.memoize.view import memoize
from zope.interface import implements
from kss.core import kssaction, KSSView
from zope.i18n import translate

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm.browser.interfaces import IWorkLocationState
from Products.plonehrm.interfaces import IWorkLocation


class AltView(BrowserView):

    def can_import_csv(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission('plonehrm: import CSV',
                                          self.context)

    def alternative_views(self):
        """List of dictionaries with url, title to alternative views.
        """
        views = []
        context_view = self.context.restrictedTraverse('@@plone_context_state')
        template_id = context_view.current_base_url().split('/')[-1]

        # default view
        if context_view.is_view_template():
            url = False
        else:
            url = context_view.canonical_object_url()
        views.append(dict(url = url,
                          title = _(u"Hired")))

        # improvement areas view
        if template_id == "improvements":
            url = False
        else:
            url = context_view.canonical_object_url() + "/improvements"
        views.append(dict(url = url,
                          title = _(u"Improvement areas")))

        # improvement areas view
        if template_id == "absence":
            url = False
        else:
            url = context_view.canonical_object_url() + "/absence"
        views.append(dict(url = url,
                          title = _(u"Absences")))

        # facebook view
        if template_id == "facebook":
            url = False
        else:
            url = context_view.canonical_object_url() + "/facebook"
        views.append(dict(url = url,
                          title = _(u"Facebook")))

        # checklist view
        if template_id == "checklist":
            url = False
        else:
            url = context_view.canonical_object_url() + "/checklist"
        views.append(dict(url = url,
                          title = _(u"Tasks")))


        # inactive employees view
        if template_id == "inactive_employees":
            url = False
        else:
            url = context_view.canonical_object_url() + "/inactive_employees"
        views.append(dict(url = url,
                          title = _(u"Dismissed")))


        if self.can_import_csv():
            # inactive employees view
            if template_id == "import_csv":
                url = False
            else:
                url = context_view.canonical_object_url() + "/import_csv"
            views.append(dict(url = url,
                              title = _(u"Import")))

        return views


class WorkLocationView(BrowserView):

    @property
    def active_employees(self):
        """Return list of active employees.
        """
        contentFilter = {'portal_type': 'Employee',
                         'review_state': 'active'}
        return self.context.getFolderContents(contentFilter=contentFilter)

    @property
    def inactive_employees(self):
        """Return list of inactive employees.
        """
        contentFilter = {'portal_type': 'Employee',
                         'review_state': 'inactive'}
        return self.context.getFolderContents(contentFilter=contentFilter)


class WorkLocationState(BrowserView):
    implements(IWorkLocationState)

    @memoize
    def is_worklocation(self):
        """Return whether the current context is a worklocation."""
        return IWorkLocation.providedBy(self.context)

    @memoize
    def current_worklocation(self):
        """Return the worklocation in the acquisition chain."""
        item = aq_inner(self.context)
        while (item is not None and
               not IWorkLocation.providedBy(item)):
            item = aq_parent(item)
        return item

    @memoize
    def in_worklocation(self):
        """Return if there is a worklocation in the acquisition chain."""
        if self.current_worklocation() is not None:
            return True
        return False

    @memoize
    def all_worklocations(self):
        """Return the brains of all available worklocations."""
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(portal_type='WorkLocation')
        return brains

class ChecklistInlineEditDate(BrowserView):
    """ Page called with jQuery to update an item date.
    """
    def __call__(self):
        if 'date' in self.request:
            date = self.request.date
        else:
            return

        if 'item_id' in self.request:
            item_id = self.request.item_id
        else:
            return

        # We get the item
        ids = item_id.split('-')
        if not len(ids) == 2:
            return

        # We get the employee.
        catalog = getToolByName(self.context, 'portal_catalog')
        employees = catalog.searchResults(portal_type='Employee')
        employee = None

        for emp in employees:
            if emp.UID == ids[0]:
                employee = emp.getObject()

        if not employee:
            return

        # We get the item
        try:
            checklist = employee['checklist']
        except:
            return

        item = checklist.findItem(id=int(ids[1]))
        if not item:
            return

        # We get a date that can be used
        if date:
            date_split = date.split('-')
            if not len(date_split) == 3:
                return

            date = "%s/%s/%s" % (date_split[2],
                                 date_split[1],
                                 date_split[0])
            date = DateTime(date)

        item.date = date

        msg = _(u'msg_checklist_inline_done',
                u'Due date has been updated')

        props = getToolByName(self.context, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')

        # This is ugly. But the dd element of kssPortalMessage does not
        # have id or class, so we can not directly inject text in it with
        # jQuery.
        return '<dt>Info</dt><dd>%s</dd>' % \
               translate(msg, target_language=lang)

class ChecklistView(BrowserView):
    """ Displays a page with all checklist items.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.items = {}
        self.sorted_items = []

    def can_edit_normal_items(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('plonehrm: Modify checklist',
                                     self.context)

    def can_edit_manager_items(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('plonehrm: Modify manager checklist',
                                     self.context)

    @property
    def isContextWorklocation(self):
        """ Returns True if the current context is a worklocation.
        """
        return self.context.getPortalTypeName() == 'WorkLocation'

    def make_date(self, date):
        """ Transforms a date into dd-mm-yyyy format.
        We do not use 'toLocalizedTime' for the moment, as the site might
        use other languages than Dutch (and so other date format)
        """
        def prepend_zero(value):
            if len(value) == 1:
                return '0' + value
            else:
                return value

        day = prepend_zero(str(date.day()))
        month = prepend_zero(str(date.month()))
        year = str(date.year())
        return '%s-%s-%s' % (day, month, year)

    def get_items(self):
        """ Returns a dictionnary representing the items and the objects
        we need to display (worklocation and employee)

        The dictionnary looks like this:
        { item : [employee, worklocation],
          item : ... }
        """

        # We get every checklist (we can not get directly the items).
        catalog = getToolByName(self.context, 'portal_catalog')

        checklists = [checklist.getObject() for checklist in
                      catalog.searchResults(portal_type='Checklist')
                      if self.context in aq_chain(checklist.getObject())]

        for checklist in checklists:
            for item in checklist.items:
                self.items[item] = [aq_parent(checklist),
                                    aq_parent(aq_parent(checklist))]

        # We create the sorted_items list, which will give the order
        # to read the dictionnary (dictionnaries can not be sorted).
        def employee_name_key(item):
            return item[1][0].getLastName()

        self.sorted_items = [key for key, value in
                             sorted(self.items.items(),
                                    key=employee_name_key)]
        return self.items

    def __call__(self):
        """ Process the form and shows the page again.
        """
        form = self.request.form
        catalog = getToolByName(self.context, 'portal_catalog')

        props = getToolByName(self.context, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')

        for item in form:
            # We check that the name and the value are identical, which
            # means that we are treating an checkbox item, not a date field.
            if not form[item] == item:
                continue

            # The item value defines two ids, the employee UID
            # and the item id.
            ids = item.split('-')
            if not len(ids) == 2:
                continue

            # We get the right employee
            employees = catalog.searchResults(portal_type='Employee')
            employee = None

            for emp in employees:
                if emp.UID == ids[0]:
                    employee = emp.getObject()

            if not employee:
                continue

            try:
                checklist = employee['checklist']
            except:
                continue

            checklist.checkItem(id=int(ids[1]))

            # We finally mark the item as done.
            self.context.plone_utils.addPortalMessage(translate(
                _(u'msg_items_updated',
                  u'Tasks have been marked as done.'),
                target_language=lang))

        return self.index()
