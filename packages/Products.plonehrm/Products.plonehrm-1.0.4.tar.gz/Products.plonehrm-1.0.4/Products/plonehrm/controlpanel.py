from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Int
from plone.app.controlpanel.form import ControlPanelForm

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm.config import PLONEHRM_PROPERTIES


BIRTHDAY_DAYS = PLONEHRM_PROPERTIES['birthday_notification_period']['default']
CONTRACT_EXPIRY_DAYS = \
    PLONEHRM_PROPERTIES['contract_expiry_notification_period']['default']
TRIAL_ENDING_DAYS = \
    PLONEHRM_PROPERTIES['trial_ending_notification_period']['default']


class IHRMNotificationsPanelSchema(Interface):

    birthday_notification = Bool(
        title=_(u'title_birthday_notification',
                default=u'Give birthday notification'),
        description=_(u'description_birthday_notification',
                      default= u"Give notification when a birthday nears."),
        default=True)

    birthday_notification_period = Int(
        title=_(u'title_birthday_notification_period',
                default=u'Birthday notification period'),
        description=_(u'description_birthday_notification_period',
                      default= u"Number of days before the birth day of an "
                      "Employee at which we give a notification."),
        default=BIRTHDAY_DAYS,
        required=False)

    contract_expiry_notification = Bool(
        title=_(u'title_contract_expiry_notification',
                default=u'Give contract expiry notification'),
        description=_(u'description_contract_expiry_notification',
                      default= u"Give notification when a contract nears "
                      "the expiration date."),
        default=True)

    contract_expiry_notification_period = Int(
        title=_(u'title_contract_expiry_notification_period',
                default=u'Contract expiry notification period'),
        description=_(u'description_contract_expiry_notification_period',
                      u"Number of days before the expiry of a contract "
                      "at which we give a notification."),
        default=CONTRACT_EXPIRY_DAYS,
        required=False)

    trial_ending_notification = Bool(
        title=_(u'title_trial_ending_notification',
                default=u'Give trial period ending notification'),
        description=_(u'description_trial_ending_notification',
                      default= u"Give notification when the end of the "
                      "trial period draws near."),
        default=True)

    trial_ending_notification_period = Int(
        title=_(u'title_trial_ending_notification_period',
                default=u'Trial period ending notification period'),
        description=_(u'description_trial_ending_notification_period',
                      u"Number of days before the end of the trial period "
                      "of an Employee at which we give a notification."),
        default=TRIAL_ENDING_DAYS,
        required=False)


class HRMNotificationsPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IHRMNotificationsPanelSchema)

    def __init__(self, context):
        super(HRMNotificationsPanelAdapter, self).__init__(context)
        self.portal = context
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.plonehrm_properties

    def get_birthday_notification_period(self):
        period = self.context.getProperty('birthday_notification_period',
                                          BIRTHDAY_DAYS)
        return period

    def set_birthday_notification_period(self, value):
        if value is not None and isinstance(value, int):
            self.context._updateProperty('birthday_notification_period',
                                         value)
        else:
            self.context._updateProperty('birthday_notification_period',
                                         BIRTHDAY_DAYS)

    birthday_notification_period = property(
        get_birthday_notification_period, set_birthday_notification_period)

    def get_birthday_notification(self):
        period = self.context.getProperty('birthday_notification', True)
        return period

    def set_birthday_notification(self, value):
        if value is not None:
            self.context._updateProperty('birthday_notification', bool(value))
        else:
            self.context._updateProperty('birthday_notification', True)

    birthday_notification = property(
        get_birthday_notification, set_birthday_notification)

    def get_contract_expiry_notification_period(self):
        period = self.context.getProperty(
            'contract_expiry_notification_period',
            CONTRACT_EXPIRY_DAYS)
        return period

    def set_contract_expiry_notification_period(self, value):
        if value is not None and isinstance(value, int):
            self.context._updateProperty('contract_expiry_notification_period',
                                         value)
        else:
            self.context._updateProperty('contract_expiry_notification_period',
                                         CONTRACT_EXPIRY_DAYS)

    contract_expiry_notification_period = property(
        get_contract_expiry_notification_period,
        set_contract_expiry_notification_period)

    def get_contract_expiry_notification(self):
        period = self.context.getProperty(
            'contract_expiry_notification', True)
        return period

    def set_contract_expiry_notification(self, value):
        if value is not None:
            self.context._updateProperty('contract_expiry_notification',
                                         bool(value))
        else:
            self.context._updateProperty('contract_expiry_notification', True)

    contract_expiry_notification = property(
        get_contract_expiry_notification,
        set_contract_expiry_notification)

    def get_trial_ending_notification_period(self):
        period = self.context.getProperty(
            'trial_ending_notification_period',
            TRIAL_ENDING_DAYS)
        return period

    def set_trial_ending_notification_period(self, value):
        if value is not None and isinstance(value, int):
            self.context._updateProperty('trial_ending_notification_period',
                                         value)
        else:
            self.context._updateProperty('trial_ending_notification_period',
                                         TRIAL_ENDING_DAYS)

    trial_ending_notification_period = property(
        get_trial_ending_notification_period,
        set_trial_ending_notification_period)

    def get_trial_ending_notification(self):
        period = self.context.getProperty(
            'trial_ending_notification', True)
        return period

    def set_trial_ending_notification(self, value):
        if value is not None:
            self.context._updateProperty('trial_ending_notification',
                                         bool(value))
        else:
            self.context._updateProperty('trial_ending_notification',
                                         True)

    trial_ending_notification = property(
        get_trial_ending_notification,
        set_trial_ending_notification)


class HRMNotificationsPanel(ControlPanelForm):
    form_fields = FormFields(IHRMNotificationsPanelSchema)

    label = _("Plone HRM notification settings")
    description = _("Settings for the Plone HRM notification periods.")
    form_name = _("Plone HRM notification settings")
