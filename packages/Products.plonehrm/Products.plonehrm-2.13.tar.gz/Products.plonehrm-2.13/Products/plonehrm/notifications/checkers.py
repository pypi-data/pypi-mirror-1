from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.event import notify
from zope.interface import implements
from zope.i18n import translate
import logging

from Products.plonehrm import utils as hrmutils
from Products.plonehrm.controlpanel import IHRMNotificationsPanelSchema
from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.notifications.interfaces import INotified
from plonehrm.notifications.utils import get_employees_for_checking
from Products.plonehrm import PloneHrmMessageFactory as _
from Products.plonehrm.notifications.events import BirthdayNearsEvent
from Products.plonehrm.notifications.interfaces import IPersonalDataEmailer
from Products.plonehrm.utils import next_anniversary

logger = logging.getLogger("plonehrm:")


class PersonalDataEmailer(HRMEmailer):
    implements(IPersonalDataEmailer)


def birthday_checker(object, event):
    """Check if the the birthday of Employees is nearing

    object is likely the portal, but try not to depend on that.
    """

    now = DateTime().earliestTime()
    portal = getToolByName(object, 'portal_url').getPortalObject()
    language_tool = getToolByName(portal, 'portal_languages')
    if language_tool:
        language = language_tool.getDefaultLanguage()
    else:
        language = 'en'

    
    panel = IHRMNotificationsPanelSchema(object)
    if not panel.birthday_notification:
        logger.info("Birthday notification is switched off.")
        return
    days_warning = panel.birthday_notification_period
    limit = now + days_warning
    employees = get_employees_for_checking(portal)
    for brain in employees:
        try:
            employee = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue

        birthday = employee.getBirthDate()
        if birthday is None:
            logger.debug("Birth date unknown for %s" % employee.officialName())
            logger.debug("Please fix at %s" % employee.absolute_url())
            continue

        anniversary = next_anniversary(employee)
        if now <= anniversary <= limit:
            # Check if we have already warned about this.
            notification_text = u"plonehrm: Birthday %s" % \
                                anniversary.year()           
            notification_title = translate(_(u'title_birthday_nears',
                                             mapping = {'name': employee.officialName()}),
                                           target_language = language)

            notified = INotified(employee)
            if notified.has_notification(notification_text):
                continue
            template = ZopeTwoPageTemplateFile('birthday_nears.pt')

            # We compute the age the employee will turn after this birthday.
            age = anniversary.year() - employee.getBirthDate().year()
            
            options = dict(employee_name = employee.officialName(),
                           anniversary = anniversary,
                           age = age,
                           link_text = translate(_(u'birthday_notification_link',
                                                   u'Direct link to the employee'),
                                                 target_language=language)
                           )
            addresses = hrmutils.email_adresses_of_local_managers(employee)
            recipients = (addresses['worklocation_managers'] +
                          addresses['hrm_managers'])
            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=notification_title)
            email.send()
            notify(BirthdayNearsEvent(employee))
            notified.add_notification(notification_text)
