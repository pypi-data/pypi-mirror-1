from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.event import notify
from zope.interface import implements
import logging

from Products.plonehrm import utils as hrmutils
from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.notifications.interfaces import INotified
from plonehrm.personaldata import PersonalMessageFactory as _
from plonehrm.personaldata.notifications.events import BirthdayNearsEvent
from plonehrm.personaldata.notifications.interfaces import IPersonalDataEmailer
from plonehrm.personaldata.notifications.utils import next_anniversary

log = logging.getLogger("plonehrm.personaldata:")
weeks_warning = 2

class PersonalDataEmailer(HRMEmailer):
    implements(IPersonalDataEmailer)
    # We want to override def email_to(self) here.


def birthday_checker(object, event):
    """Check if the the birthday of Employees is nearing

    object is likely the portal, but try not to depend on that.
    """
    cat = getToolByName(object, 'portal_catalog')
    now = DateTime().earliestTime()
    limit = now + (weeks_warning * 7)
    employees = cat(portal_type='Employee')
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
