import csv

from Products.Five import BrowserView
from zope.i18n import translate
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFPlone.utils import safe_unicode
from Acquisition import aq_inner

from Products.plonehrm.content.employee import Employee, Employee_schema

class CSVImport(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        # Employees created form the CSV file.
        self.created_employees = []        

        self.no_file = False
        self.invalid_file = False

    def reverse_translate(self, value, vocab_method):
        """ Try to find the database name for a value from
        its translation in the current language.
        """
        if not vocab_method in dir(Employee):
            # Should not happen.
            return value

        vocabulary = eval('Employee(self.context).%s()' % vocab_method)        
        if type(vocabulary) in [tuple, list]:
            # In this case there is no translations, so the value is the one
            # stored in the database.
            return value

        for name, label in vocabulary.items():
            if value.lower() == translate(label,
                                          context = self.request).lower():
                return name
            
        # If we arrive here, that means that we did not find a suitable
        # translation.
        return None

    def make_title(self, data):
        """ Basically a copy/paste of Employee.Title.
        """
        fields = ['firstName', 'middleName', 'lastName']
        parts = []

        for field in fields:
            if field in data:
               parts.append(data[field])

        if not parts:
            return u''

        # Filter out the empty bits:
        parts = [safe_unicode(part) for part in parts if part]
        return u' '.join(parts)


    def __call__(self):
        form = self.request.form

        # The form has not been submitted.
        if not 'file' in form:
            return self.index()

        if not form['file']:
            self.no_file = True
            return self.index()

        data = csv.DictReader(form['file'])

        # A dictionnary representing employee fields and their translation
        # in the current language.
        # The key is the translation and the value is the field created in
        # the schema.
        employee_fields = {}
        for field in Employee_schema.fields():
            field_translation = translate(field.widget.label,
                                          context=self.request)
            
            employee_fields[field_translation] = field

        row = data.next()
        while row:
            # We build a dictionnary that looks like those
            # received when submitting a form.
            emp_data = {}
            for item in row:
                field = None
                for emp_f in employee_fields:
                    if emp_f.lower() == item.lower():
                        field = employee_fields[emp_f]
                        break

                if not field:
                    continue
                
                # Check if we have to translate the field.
                if field.vocabulary:
                    value = self.reverse_translate(row[item],
                                                   field.vocabulary)
                else:
                    value = row[item]

                emp_data[field.getName()] = value
                
            emp_data['title'] = self.make_title(emp_data)
            context = aq_inner(self.context)
            
            new_id = context.generateUniqueId('Employee')
            context.invokeFactory("Employee", id=new_id,
                                  title=emp_data['title'])

            new_emp = getattr(context, new_id)

            # We store the informations.
            new_emp.update(**emp_data)            

            new_emp._renameAfterCreation()
            new_emp.unmarkCreationFlag()
            notify(ObjectInitializedEvent(new_emp))

            self.created_employees.append(new_emp)

            try:
                row = data.next()
            except:
                row=None

        return self.index()
