from Products.CMFPlone import Batch
from Products.Five import BrowserView
from Products.plonehrm import PloneHrmMessageFactory as _


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
                          title = _(u"Active")))

        # inactive employees view
        if template_id == "inactive_employees":
            url = False
        else:
            url = context_view.canonical_object_url() + "/inactive_employees"
        views.append(dict(url = url,
                          title = _(u"Inactive")))

        # improvement areas view
        if template_id == "improvements":
            url = False
        else:
            url = context_view.canonical_object_url() + "/improvements"
        views.append(dict(url = url,
                          title = _(u"Improvement areas")))

        return views


class WorkLocationView(BrowserView):

    @property
    def active_employees(self):
        """Return list of active employees.
        """
        contentFilter = {'portal_type':'Employee',
                         'review_state':'active'}
        return self.context.getFolderContents(contentFilter=contentFilter)

    @property
    def inactive_employees(self):
        """Return list of inactive employees.
        """
        contentFilter = {'portal_type':'Employee',
                         'review_state':'inactive'}
        return self.context.getFolderContents(contentFilter=contentFilter)

    @property
    def managementFiles(self):
        """Return list of management files.
        """
        contentFilter = {'portal_type':'ManagementFile'}
        return self.context.getFolderContents(contentFilter=contentFilter)

    @property
    def extraItems(self):
        all = self.context.getFolderContents()
        rest = [item for item in all
                if item['portal_type'] not in ['Employee', 'ManagementFile']]
        # Turn 'rest' into a batch for the benefit of the tabular folder
        # macro.
        b_start = 0
        b_size = 20
        rest = Batch(rest, b_size, b_start, orphan=0)
        return rest
