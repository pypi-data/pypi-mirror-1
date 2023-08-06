from kss.core import kssaction, KSSView
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS
from Products.CMFCore import utils as cmfutils
from Acquisition import aq_inner

from Products.plonehrm import PloneHrmMessageFactory as _

class FileKssView(KSSView):
    """ Class managing the 'File' viewlet.
    """

    def _findUniqueId(self, id):
        """Find a unique id in this context.

        This is based on the given id, by appending -n, where n is a
        number between 1 and the constant
        RENAME_AFTER_CREATION_ATTEMPTS, set in
        Archetypes/config.py. If no id can be found, return None.

        Method is slightly adapted from Archetypes/BaseObject.py

        Most important changes:

        - Do not rename image.jpg to image.jpg-1 but image-1.jpg

        - If no good id can be found, just return the original id;
          that way the same errors happens as would without any
          renaming.

        This method was written for the PloneFlashUpload product:
        http://plone.org/products/ploneflashupload
        """
        context = aq_inner(self.context)
        ids = context.objectIds()
        valid_id = lambda id: id not in ids

        if valid_id(id):
            return id

        # 'image.name.gif'.rsplit('.', 1) -> ['image.name', 'gif']
        splitted = id.rsplit('.', 1)
        if len(splitted) == 1:
            splitted.append('')
        head, tail = splitted

        idx = 1
        while idx <= RENAME_AFTER_CREATION_ATTEMPTS:
            if tail:
                new_id = '%s-%d.%s' % (head, idx, tail)
            else:
                new_id = '%s-%d' % (head, idx)
            if valid_id(new_id):
                return new_id
            idx += 1

        # Just return the id.
        return id

    def replaceViewlet(self, show_list = True):
        """ As code to display form or list is almost the same,
        we factorise the code in this method.
        The show_list parameter is used to know if we display the
        field list or the upload form instead.
        """

        # First, we get the viewlet manager.
        view = self.context.restrictedTraverse('@@plonehrm.files')

        # We configure it.
        view.show_list = show_list

        # We get the content displayed by in the viewlet.
        rendered = view.render()

        # We replace the content of the viewlet by the new one.
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('plonehrmFileViewlet')
        core.replaceHTML(selector, rendered)

    @kssaction
    def display_form(self):
        """ This action is used to display the add form
        in the viewlet.
        """
        self.replaceViewlet(False)

    @kssaction
    def display_list(self):
        """ This action is used to display the list of files.
        """
        self.getCommandSet('plone').issuePortalMessage('')
        self.replaceViewlet(True)

    def add_file(self):
        """ This action is called when adding a new file. This action is
        not called with KSS, but directly after submitting the form.
        """

        # Tests if the page '*/kss_add_file/' has been called directly,
        # in this case, we redirect to the context view.
        if not 'new_file_file' in self.request.form:
            self.request.response.redirect(self.context.absolute_url())
            return

        # If no file has been provided, then we redirect to
        # the employee view.
        # Note: this shall not append, as there is a Javascript validation
        # on the form and the form can only be shown with Javascript.
        # So this should only append if the user disable Javascript once the
        # form is displayed.
        if not self.request.new_file_file:
            self.request.response.redirect(self.context.absolute_url())
            return

        # We get the uploaded file.
        uploaded_file = self.request.new_file_file
        filename = uploaded_file.filename
        file_desc = self.request.form['file_desc']

        # If no title has been specified, we use the filename as title.
        if self.request.form['file_title']:
            file_title = self.request.form['file_title']
        else:
            file_title = filename

        # We create the file.
        plone_tool = cmfutils.getToolByName(self.context, 'plone_utils')
        new_id = plone_tool.normalizeString(filename)
        new_id = self._findUniqueId(new_id)

        self.context.invokeFactory('File',
                                   id=new_id,
                                   title=filename)

        new_file = getattr(self.context, new_id)
        new_file.setFile(uploaded_file)
        new_file.setTitle(file_title)
        new_file.setDescription(file_desc)

        new_file.unmarkCreationFlag()
        new_file._renameAfterCreation()
        notify(ObjectInitializedEvent(new_file))

        self.context.plone_utils.addPortalMessage(_(u'msg_file_added',
                                                    u'File added'))


        # We redirect to the employee view.
        self.request.response.redirect(self.context.absolute_url())
