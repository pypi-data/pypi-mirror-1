from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.i18n import translate


class BaseEditView(BrowserView):
    """ This view allows to create simple edit form for Archetype objects.
        It does not create all special archetype stuff, but focuses
        on the essential fields as defind in the schema.

        Some methods have to be defined in the child classes:

        get_errors_list which provides the list of potential errors.
        get_form_fields which provides the list of fields in the form.
        validate_form which validates the form and updates the list of errors.

        pre_udate is called before the object is saved.
        post_update is called after the object is saved.
    """

    def lang(self):
        """ The user's language.
        """
        props = getToolByName(self.context, 'portal_properties')
        return props.site_properties.getProperty('default_language')

    def translate_field_name(self, name):
        """ Returns the label of a field.
        """
        for field in self.schema.fields():
            if field.getName() == name:
                return translate(field.widget.label,
                                 target_language=self.lang())

    def translate_vocabulary(self, vocab, msg_factory):
        """ Transform a vocabulary into a dictionnary where values are
        translated according to the user's language.
        """
        res = {}
        # Weird case when vocabulary are defined as tuple.
        # No tranlsation is possible in this case.
        if type(vocab) == tuple:
            for key in vocab:
                res[key] = key
            return res

        lang = self.lang()
        for key, value in vocab.items():
            res[key] = translate(msg_factory(value),
                                   target_language = lang)
        return res

    def get_vocabulary(self, field):
        """ Returns the translated vocabulary for a given field.        
        """
        accessor = 'get_' + field + '_vocabulary'
        if not accessor in dir(self):
            return {}

        return eval('self.' + accessor + '()')
    
    def get_errors_list(self):
        """ The list of potential errors to display in the form.

        Returns a dictionnary looking like this:
        {first_field_name : {first_error_name : first_error_text,
                             second_error_name : second_error_text},
         second_field_name : {...}}
        """
        pass

    def get_form_fields(self):
        """ Provides the list of fields that should be present in
        the form
        """
        return [f.getName() for f in self.schema.fields()]

    def get_required_fields(self):
        """ Provides the list of fields that are required. This does not
        have any effect on validation, just in the way form is displayed.        
        """
        return []
    
    def validate_form(self):
        """ Validates the submitted form and updates the error list.
        """
        pass

    def pre_update(self):
        """ Called before saving the object.
        """
        pass

    def post_update(self):
        """ Called after the object is saved.
        """
        pass

    def __init__(self, context, request, schema=None,
                 success_message=None, error_message=None):
        """ schema is the Archetype schema of the object to edit.
            successMessage is the status message displayed if edition worked,
            error_message the one displayed when errors occured.
        """
        self.context = context
        self.request = request
        self.schema = schema
        self.success_message = translate(success_message,
                                         target_language=self.lang)
        self.error_message = translate(error_message,
                                         target_language=self.lang)

        # The list of fields
        self.form_fields = self.get_form_fields()

        # The list of required fields.
        self.required_fields = self.get_required_fields()

        self.form = self.request.form
        # Load the form with data from the instance
        if len(self.form) == 1:
            self.form_submitted = False
            for field in self.form_fields:
                accessor = 'get' + field.capitalize()

                if accessor in dir(self.context):
                    self.form[field] = eval('self.context.' + accessor + '()')
                else:
                    if field in dir(self.context):
                        self.form[field] = eval('self.context.' + field)                    
        else:
            self.form_submitted = True

        # List of potential errors.
        self.errors_list = self.get_errors_list()
        
        # Error messages that shall be displayed.
        self.errors = []

    def next_url(self):
        """ Returns the url of the page displayed when object has been saved.
        """
        return self.context.absolute_url()

    def __call__(self):
        if 'form_cancel' in self.form:
            self.request.response.redirect(self.context.absolute_url())
        
        if not self.form_submitted:
            return self.index()
            
        self.validate_form()
        if self.errors:
            self.context.plone_utils.addPortalMessage(self.error_message,
                                                      type='Error')
            return self.index()

        self.pre_update()
        self.context.update(**self.form)
        self.post_update()
        
        self.context.plone_utils.addPortalMessage(self.success_message)
        
        self.request.response.redirect(self.next_url())
        
