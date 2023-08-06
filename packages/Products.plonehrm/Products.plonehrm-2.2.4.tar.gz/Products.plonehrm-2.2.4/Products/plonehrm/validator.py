from Products.validation.interfaces import ivalidator
from DateTime import DateTime
from zope.i18n import translate
from Products.plonehrm import PloneHrmMessageFactory as _


class DateValidator:
    __implements__ = (ivalidator, )

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        now = DateTime()
        value = DateTime(value)
        if value > now:
            if value.year() > now.year():
                error = _("Date is supposed to be in the past, "
                          "please enter a valid year.")
            elif value.month() > now.month():
                error = _("Date is supposed to be in the past, "
                          "please enter a valid month.")
            elif value.day() > now.day():
                error = _("Date is supposed to be in the past, "
                          "please enter a valid day.")
            else:
                error = ''
            if error:
                return translate(error, context=kwargs['REQUEST'])
        return True


class AgeValidator:
    __implements__ = (ivalidator, )

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        now = DateTime()
        value = DateTime(value)

        if value.year() > now.year()-12:
            error = _("You are too young")
            return translate(error, context=kwargs['REQUEST'])
        return True
