from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch
from Products.Five import BrowserView
from plone.memoize.view import memoize
from zope.interface import implements

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm.browser.interfaces import IWorkLocationState
from Products.plonehrm.interfaces import IWorkLocation


class AltView(BrowserView):

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

        # inactive employees view
        if template_id == "inactive_employees":
            url = False
        else:
            url = context_view.canonical_object_url() + "/inactive_employees"
        views.append(dict(url = url,
                          title = _(u"Dismissed")))

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
                          title = _(u"Absence")))


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
