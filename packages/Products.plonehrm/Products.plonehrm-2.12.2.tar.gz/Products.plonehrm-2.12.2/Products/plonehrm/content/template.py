from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType

from Products.plonehrm.config import PROJECTNAME
from Products.plonehrm import PloneHrmMessageFactory as _

TemplateSchema = ATDocumentSchema.copy() + Schema((
    StringField(
        name='type',
        required=True,
        vocabulary=['undefined', 'contract', 'letter',
                    'job_performance', 'absence_evaluation'],
        widget=SelectionWidget(
            label=_(u'label_templateType',
                    default=u'Template type'),
            ),
        ),
    ),                                                           

)

for schema_key in TemplateSchema.keys():
    if not TemplateSchema[schema_key].schemata == 'default':
        TemplateSchema[schema_key].widget.visible={'edit':'invisible',
                                                   'view':'invisible'}


class Template(ATDocument):
    """ This archetype is used to store every templates that can be
    defined in plone HRM:
     - contracts templates
     - letter templates
     - job performance templates
     - absence evaluation templates
    """
    schema = TemplateSchema
    meta_type = "Template"


registerType(Template, PROJECTNAME)
