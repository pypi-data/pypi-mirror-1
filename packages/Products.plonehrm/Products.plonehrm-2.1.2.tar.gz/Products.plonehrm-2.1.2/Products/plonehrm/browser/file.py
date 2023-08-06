from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet


class FileViewlet(Explicit):
    implements(IViewlet)
    render = ViewPageTemplateFile('file.pt')

    def __init__(self, context, request, view, manager):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

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
        return self.context.contentValues(
            filter=dict(portal_type=('File', 'Image')))
