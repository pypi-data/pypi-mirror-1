import logging

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.i18n import translate

from Products.plonehrm.utils import email_adresses_of_local_managers
from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.checklist import ChecklistMessageFactory as _

logger = logging.getLogger("plonehrm.checklist:checker")


def checklist_notifications(object, event):
    """Check if there are notifications that need to be sent.

    Send an email for each of the checklist items that have the
    notification flag set. The email will be sent to the HRM manager
    OR the email address spcified on the checklist item.

    NOTE: This function will only send emails for checklist items that
    are due today!
    """
    logger.info('checklist notification checker activated.')

    portal = getToolByName(object, 'portal_url').getPortalObject()
    catalog = getToolByName(portal, 'portal_catalog')
    query = {'portal_type': 'Checklist'}
    checklists = catalog(query)
    language_tool = getToolByName(portal, 'portal_languages')
    if language_tool:
        language = language_tool.getDefaultLanguage()
    else:
        language = 'en'

    def send_mail(employee, item):
        addresses = email_adresses_of_local_managers(employee)
        recipients = addresses['hrm_managers']
        if item.email:
            recipients = [item.email]
        template = ZopeTwoPageTemplateFile('checklist_item.pt')
        # TODO: Currently the checklist item text is stored as a
        # string instead of unicode. Decoding it here in a rather
        # crude way now because I believe it should be solved at the
        # source by storing it in unicode from the start.
        subject = translate(_(u'title_checklist_is_due',
                              u'Task "${task}" is due today',
                              mapping = {'task': item.text.decode('utf8')}),
                            target_language = language)
        link_text = translate(_(u'title_go_to_notification',
                                u'Go to ${name}',
                                mapping = {'name': employee.Title()}),
                              target_language = language)
        options = dict(employee=employee,
                       task=item,
                       title=subject,
                       link_text=link_text)
        email = HRMEmailer(employee,
                           template=template,
                           options=options,
                           recipients=recipients,
                           subject=subject)
        email.send()


    for checklist in checklists:
        try:
            checklist = checklist.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", checklist.getURL())
            continue

        employee = aq_parent(checklist)

        for item in checklist.items:
            # We only send notifications if the due date is today!
            if item.notification and item.date and item.date.isCurrentDay():
                send_mail(employee, item)
