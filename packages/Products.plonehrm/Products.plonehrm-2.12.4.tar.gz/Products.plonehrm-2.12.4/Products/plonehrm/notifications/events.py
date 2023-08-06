from zope.i18n import translate
from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from Products.CMFCore.utils import getToolByName

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm.notifications.interfaces import IPersonalDataEvent
from Products.plonehrm.utils import next_anniversary


class BirthdayNearsEvent(ObjectEvent):
    """Employee is almost having his birthday.
    """
    implements(IPersonalDataEvent)

    # Does a (HRM) Manager need to handle it?
    for_manager = False

    def __init__(self, *args, **kwargs):
        super(BirthdayNearsEvent, self).__init__(*args, **kwargs)
        birthdate = self.object.getBirthDate()
        anniversary = next_anniversary(self.object)
        age = anniversary.year() - birthdate.year()
        anniversary = self.object.restrictedTraverse('@@plone').toLocalizedTime(anniversary)
        text = _(u"Turns ${age} at ${anniversary}.",
                 mapping=dict(age=age,
                              anniversary=anniversary))
        props = getToolByName(self.object, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')
        self.message = translate(text, target_language=lang)
