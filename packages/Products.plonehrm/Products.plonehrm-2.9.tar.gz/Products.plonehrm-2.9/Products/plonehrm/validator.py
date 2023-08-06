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
        if not value:
            return True

        now = DateTime()
        try:
            value = DateTime(value)
        except:
            error = _("error_invalid_date")
            return translate(error, context=kwargs['REQUEST'])           

        if value.year() > now.year()-12:
            error = _("You are too young")
            return translate(error, context=kwargs['REQUEST'])
        return True


class BSNValidator:
    """ This validator ensures that a BSN number is valid.
    It takes as input a string, composed of digits and dots. It returns
    True if the value is a correct BSN number and a string indicating the
    problem in the other cases.

    XXX Note: this is valid for Dutch SOFI/BurgerServiceNumbers.  We
    may want to let this work for other countries as well.


    We create an instance of the validator.
    >>> bsnValid = BSNValidator('bsn')

    Now we check its behavior.

    It first removes the dots form the string.
    >>> bsnValid.remove_dots('')
    ''
    >>> bsnValid.remove_dots('123')
    '123'
    >>> bsnValid.remove_dots('.123')
    '123'
    >>> bsnValid.remove_dots('123.')
    '123'
    
    >>> bsnValid.remove_dots('1.2.3')
    '123'
    >>> bsnValid.remove_dots('.')
    ''
    >>> bsnValid.remove_dots('..')
    ''

    Then it checks the length of the string and that it contains only
    valid characters.

    This one contains an invalid character.
    >>> bsnValid.validate('123.45.6a.38')
    u'bsn_validation_bad_input'

    This one too.
    >>> bsnValid.validate('123.45.67,38')
    u'bsn_validation_bad_input'

    This one could be valid if it was long enough
    >>> bsnValid.validate('16.51')
    u'bsn_validation_bad_length'

    Then, it computes the sum of digits, multiplied by their rank.
    For example, it the BSN number is ac.bd.ef.ghi, the sum will be
    a*9 + b*8 + c*7 + d*6 + e*5 + f*4 + g*3 + h*2 + i*-1
    (note the minus for the last digit)

    >>> bsnValid.make_number_sum(0)
    0
    >>> bsnValid.make_number_sum(1)
    -1

    This shall return 4*3 + 5*2 + 6*-1
    >>> bsnValid.make_number_sum(456)
    16

    >>> bsnValid.make_number_sum(32154876)
    117

    Just to check.
    >>> 6*-1 + 7*2 + 8*3 + 4*4 + 5*5 + 1*6 + 2*7 + 3*8
    117

    With a supposedly real BSN.
    >>> bsnValid.make_number_sum(736160231)
    176

    If the sum of the number can be divided by 11, then the number is correct.

    This one is correct.
    >>> bsnValid.validate('73.61.60.231')
    True

    It is still correct with a 0 at the beginning.
    >>> bsnValid.validate('073.61.60.231')
    True

    This one is not correct.
    >>> bsnValid.validate('073.61.60.221')
    u'bsn_validation_failed'

    """
    __implements__ = (ivalidator, )    

    def remove_dots(self, value):
        """ This method removes dots from a string.
        We assume that the BSN number entered by the user only
        contains digits and dots.
        """

        return ''.join(value.split('.'))

    def make_number_sum(self, value):
        """ Compute the sum of digits in a number multiplied by their rank.

        Only some numbers are valid.  Each digit gets multiplied
        depending on its position.
        """

        # special case for the last digit: multiply by a negative number
        total = (value % 10) * -1
        value = value / 10
        for i in range(2, 11):
            total += i * (value % 10)
            value = value / 10

        return total

    def validate(self, value):
        """ Validates a BSN number. Returns True if the value is a valid
        BSN number or a message instead.

        We extracted this function to allow unitary testing.
        """

        # First, we remove the dots.
        value = self.remove_dots(value)

        # Then we check the length of the string. We do it before casting
        # it into an integer, as we might lose the first zeros.
        if not len(value) in [9, 10]:
            return _(u'bsn_validation_bad_length',
                     u'BSN numbers are supposed to have 9 or 10' + \
                     ' characters (excluding dots).')

        # Now we cast it and ensures that  there is only digits in the string.
        try:
            value = int(value)
        except:
            return _(u'bsn_validation_bad_input',
                     u'The BSN number can only contain digits and dots.')

        total = self.make_number_sum(value)

        if total % 11 == 0:
            return True

        return _(u'bsn_validation_failed',
                 u'This is not a valid BSN number.')

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        result = self.validate(value)

        if result == True:
            return True
        else:
            return translate(result, context=kwargs['REQUEST'])
