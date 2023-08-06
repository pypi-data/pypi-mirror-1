from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet


class FileViewlet(Explicit):
    implements(IViewlet)
    render = ViewPageTemplateFile('file.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

        # This attribute is used to know how the viewlet is
        # displayed.
        # If True, the list of File is displayed. If false,
        # the upload form is displayed.
        self.show_list = True

    def update(self):
        pass

    def add_url(self):
        """ Add new file
        """
        # check Add permission on employee
        # return None if we don't have permission
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission('ATContentTypes: Add File', self.context):
            url = self.context.absolute_url() + '/createObject?type_name=File'
            return url

    def file_list(self):
        # Return image too while we are at it.
        contentFilter = {'portal_type': ('File', 'Image')}
        brains = self.context.getFolderContents(contentFilter=contentFilter)

        def date_key(item):
            return item['created']

        items = sorted(brains, key=date_key)
        items.reverse()
        return items
