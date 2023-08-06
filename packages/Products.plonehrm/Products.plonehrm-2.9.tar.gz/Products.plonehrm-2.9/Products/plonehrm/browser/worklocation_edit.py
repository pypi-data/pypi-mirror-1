from zope.i18n import translate

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm.content.worklocation import WorkLocation
from Products.plonehrm.content.worklocation import schema
from Products.plonehrm.browser.base_edit import BaseEditView

class WorklocationEditView(BaseEditView):
    """ Special view to edit worklocation.
    """

    def translate_field_name(self, name):
        if not name in self.form_fields:
            # Should not happen.
            return

        if name == 'title':
            return translate(_(u'plonehrm_label_trade_name'),
                             target_language=self.lang())

        if name == 'hasInsurance':
            return translate(_(u'plonehrm_label_has_insurance',
                               default='The worklocation has an insurance'),
                             target_language=self.lang())

        # Seek the field in the schema.
        for field in schema.fields():
            if field.getName() == name:
                return translate(field.widget.label,
                                 target_language=self.lang())

    def get_pay_period_vocabulary(self):
        """ Returns the vocabulary for payPeriod in a simplified dictionnary,
        in which keys are the possible values and the values are the translated
        labels.
        """
        vocab = self.context._payPeriodVocabulary()
        return self.translate_vocabulary(vocab, _)

    def get_required_fields(self):
        return ['title', 'insuranceName', 'insuranceNumber']

        
    def get_errors_list(self):
        """ The list of potential errors to display in the form.
        """
        lang = self.lang()
        
        # The list of potentials errors for each field.
        no_title = translate(_(u'msg_error_no_title',
                               default=u'You must provide a trade name for' + \
                               ' the worklocation'),
                             target_language=lang)

        vacation_no_int = translate(_(u'msg_error_vacation_no_int',
                                      default=u'Vacation days lenght has to' +\
                                      ' be an integer'),
                                    target_language=lang)

        no_insurance = translate(_(u'msg_error_no_insurance',
                                   default=u'You must provide an insurance name'
                                   ),
                                 target_language=lang)

        no_number = translate(_(u'msg_error_no_insurance_number',
                                default=u'You must provide an ' +\
                                'insurance number'),
                              target_language=lang)

                             
        return {'title' : {'no_title': no_title},
                'vacationDays' : {'no_int' : vacation_no_int},
                'insuranceName' : {'no_name' : no_insurance},
                'insuranceNumber' : {'no_number' : no_number}}


    def get_form_fields(self):
        """ Provides the list of fields that should be present in
        the form
        """
        fields = ['title']
        fields.extend([f.getName() for f in schema.fields()])
        
        # Adds a special field (hasInsurance) before 'insuranceName'
        if 'insuranceName' in fields:
            fields.insert(fields.index('insuranceName'), 'hasInsurance')

        return fields

    def validate_form(self):
        """ Validates the form submitted when updating the worklocation.
        """
        fields = self.get_form_fields()
        for field in fields:
            if not field in self.form and \
                not field in ['hasInsurance', 'payPeriod']:
                # Should not happen
                return

        errors = []
        if not self.form['title']:
            self.errors.append('title_no_title')

        if self.form['vacationDays']:
            try:
                int(self.form['vacationDays'])
            except ValueError:
                self.errors.append('vacationDays_no_int')

        if self.form['hasInsurance']:
            if not self.form['insuranceName']:
                self.errors.append('insuranceName_no_name')

            if not self.form['insuranceNumber']:
                self.errors.append('insuranceNumber_no_number')

        if 'payPeriod' in self.form:
            if not self.form['payPeriod'] in self.get_pay_period_vocabulary():
                # Should not happen.
                self.form['payPeriod'] = ''


    def __init__(self, context, request):
        success_msg = _(u'msg_worklocation_saved',
                        default=u'The worklocation has been saved.')

        error_msg = _(u'error_worklocation_saved',
                        default=u'Errors were found while saving the worklocation.')

        BaseEditView.__init__(self, context, request, schema,
                              success_msg, error_msg)

        # We add our special field which is not described in the schema.
        if not 'hasInsurance' in self.form:
            self.form['hasInsurance'] = bool(self.form['insuranceName'])

        # Pay period is a radio button and so might not be in the form
        # if no value has been selected.
        if not 'payPeriod' in self.form:
            self.form['payPeriod'] = None
