from datetime import date, timedelta
import logging

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.plonehrm.utils import email_adresses_of_local_managers
from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.flags import *
from plonehrm.absence.interfaces import IAbsenceAdapter
from plonehrm.absence.notifications.events import *
from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.notifications.interfaces import INotified
from plonehrm.notifications.utils import get_employees_for_checking
from zope.event import notify


logger = logging.getLogger('plonehrm.absence:checker:')


def current_date():
    """Helper to find the current date -
    conveniently easy to mock for testing. :) """
    return date.today()


def sick_period_checker(object, event):
    """Check the period Employees are sick, sending appropriate notifications.
    """
    logger.info('sick period checker activated.')

    def weeks(num):
        """Readability helper"""
        return timedelta(num*7)

    def send_mail(template_file, subject, employee):
        options = dict(employee=employee)
        template = ZopeTwoPageTemplateFile(template_file)
        addresses = email_adresses_of_local_managers(employee)
        recipients = (addresses['worklocation_managers'] +
                      addresses['hrm_managers'])
        email = HRMEmailer(employee,
                           template=template,
                           options=options,
                           recipients=recipients,
                           subject=subject)
        email.send()


    employees = get_employees_for_checking(object)
    for brain in employees:
        employee = brain.getObject()
        absencedata = IAbsenceAdapter(employee).current_absence()

        if absencedata:
            notified = INotified(employee)
            stages = [
                ((1, 2),
                 _(u"Employee sick - 1 week"),
                 'absenceweek1email.pt',
                 ABSENCEWEEK1_NOTIFICATION,
                 AbsenceWeek1Event),
                ((5, 6),
                 _(u"Problem analysis - 6 weeks"),
                 'absenceweek6email.pt',
                 ABSENCEWEEK6_NOTIFICATION,
                 AbsenceWeek6Event),
                ((7, 8),
                 _(u"Plan of action - 8 weeks"),
                 'absenceweek8email.pt',
                 ABSENCEWEEK8_NOTIFICATION,
                 AbsenceWeek8Event),
            ]

            start_date = absencedata.start_date.date()
            for stage in stages:

                weekcount, subject, template, notification_id, event = stage
                notification_start = start_date + weeks(weekcount[0])
                notification_end = start_date + weeks(weekcount[1])

                if notification_start <= current_date() <= notification_end:
                    if notified.has_notification(notification_id):
                        continue
                    send_mail(template, subject, employee)
                    notify(event(employee, subject=subject))
                    notified.add_notification(notification_id)

            # After 8 weeks we begin a 6-week cycle of meetings with the
            # employee
            length = current_date() - start_date
            if (length - weeks(14)).days % weeks(6).days == 0:
                weekcount = str((current_date() - start_date).days / 7)
                subject = _(
                    u'Update reintegration file. Week: ${week}',
                    mapping={'week': weekcount})
                if notified.has_notification(
                    ABSENCE6WEEKREPEAT_NOTIFICATION + weekcount):
                    continue
                send_mail('absence6weekrepeatemail.pt', subject, employee)
                notify(Absence6WeekRepeatEvent(employee, subject=subject))
                notified.add_notification(
                    ABSENCE6WEEKREPEAT_NOTIFICATION + weekcount)
