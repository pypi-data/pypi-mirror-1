from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.event import notify
from zope.interface import implements
import logging

from Products.plonehrm import utils as hrmutils
from Products.plonehrm.controlpanel import IHRMNotificationsPanelSchema
from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.notifications.interfaces import INotified
from plonehrm.notifications.utils import get_employees_for_checking
from plonehrm.personaldata import PersonalMessageFactory as _
from plonehrm.personaldata.notifications.events import BirthdayNearsEvent
from plonehrm.personaldata.notifications.interfaces import IPersonalDataEmailer
from plonehrm.personaldata.notifications.utils import next_anniversary

log = logging.getLogger("plonehrm.personaldata:")


class PersonalDataEmailer(HRMEmailer):
    implements(IPersonalDataEmailer)


def birthday_checker(object, event):
    """Check if the the birthday of Employees is nearing

    object is likely the portal, but try not to depend on that.
    """
    now = DateTime().earliestTime()
    portal = getToolByName(object, 'portal_url').getPortalObject()
    panel = IHRMNotificationsPanelSchema(object)
    if not panel.birthday_notification:
        log.info("Birthday notification is switched off.")
        return
    days_warning = panel.birthday_notification_period
    limit = now + days_warning
    employees = get_employees_for_checking(portal)
    for brain in employees:
        employee = brain.getObject()
        personal = employee.personal
        birthday = personal.getBirthDate()
        if birthday is None:
            log.warn("Birth date unknown for %s" % employee.officialName())
            log.warn("Please fix at %s" % employee.absolute_url())
            continue

        anniversary = next_anniversary(employee)
        if now <= anniversary <= limit:
            # Check if we have already warned about this.
            notification_text = u"plonehrm.personaldata: Birthday %s" % \
                                anniversary.year()
            notified = INotified(personal)
            if notified.has_notification(notification_text):
                continue
            template = ZopeTwoPageTemplateFile('birthday_nears.pt')
            options = dict(employee_name = employee.officialName(),
                           anniversary = anniversary)
            addresses = hrmutils.email_adresses_of_local_managers(employee)
            recipients = (addresses['worklocation_managers'] +
                          addresses['hrm_managers'])
            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=_(u'Birthday of ${name}',
                                         mapping=dict(name=employee.Title())))
            email.send()
            notify(BirthdayNearsEvent(employee))
            notified.add_notification(notification_text)
