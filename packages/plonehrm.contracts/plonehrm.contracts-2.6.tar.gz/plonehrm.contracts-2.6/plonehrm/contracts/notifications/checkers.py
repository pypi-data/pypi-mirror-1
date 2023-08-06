import logging

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from zope.i18n import translate

from Products.plonehrm import utils
from Products.plonehrm.controlpanel import IHRMNotificationsPanelSchema
from Products.plonehrm import PloneHrmMessageFactory as _hrm

from plonehrm.contracts import ContractsMessageFactory as _
from plonehrm.contracts.notifications.events import ContractEndingEvent
from plonehrm.contracts.notifications.events import TrialPeriodEndingEvent

from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.notifications.interfaces import INotified
from plonehrm.notifications.utils import get_employees_for_checking
from zope.event import notify

logger = logging.getLogger("plonehrm.contracts:")

EXPIRY_NOTIFICATION = u"plonehrm.contracts: Expiry notification"
TRIAL_PERIOD_ENDING_NOTIFICATION = u"plonehrm.contracts: Trial period ending"


def contract_ending_checker(object, event):
    """Check if the last contract of employees is almost ending.

    object is likely the portal, but try not to depend on that.
    """
    portal = getToolByName(object, 'portal_url').getPortalObject()
    panel = IHRMNotificationsPanelSchema(object)
    if not panel.contract_expiry_notification:
        logger.info("Contract ending notification is switched off.")
        return
    days_warning = panel.contract_expiry_notification_period

    language_tool = getToolByName(portal, 'portal_languages')
    if language_tool:
        language = language_tool.getDefaultLanguage()
    else:
        language = 'en'

    employees = get_employees_for_checking(object)
    for brain in employees:
        try:
            employee = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue

        last_contract = employee.get_last_contract()

        info = dict(employee_name = employee.officialName(),
                    employee_url = employee.absolute_url())
        if last_contract is None:
            continue

        expires = last_contract.expiry_date()
        if expires is None:
            continue

        addresses = utils.email_adresses_of_local_managers(employee)
        recipients = (addresses['worklocation_managers'] +
                      addresses['hrm_managers'])


        if (expires + 1).isCurrentDay():
            # The last contract expired yesterday.
            link_text = translate(_hrm(u'title_go_to_employee',
                                       mapping = {'name': employee.Title()}),
                                  target_language = language)

            options = {'link_href': employee.absolute_url(),
                       'link_text': link_text}

            template = ZopeTwoPageTemplateFile('no_current_contract.pt')

            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=_(u'title_no_current_contract',
                                         mapping={'name': employee.officialName()}))
            email.send()

            continue

        now = DateTime()       
        if now + days_warning >= expires:
            # Check if we have already warned about this.
            notified = INotified(last_contract)
            if notified.has_notification(EXPIRY_NOTIFICATION):
                continue
            info['days'] = days_warning
            options = dict(days=days_warning)

            worklocation = aq_parent(employee)

            link_href = employee.absolute_url() + '/createObject?type_name='
            if worklocation.getCreateLetterWhenExpiry():
                link_href += 'Letter'
                link_text = _('Create a new letter')
            else:
                link_href += 'Contract'
                link_text = _('Create a new contract')                

            options['link_href'] = link_href
            options['link_text'] = link_text
            
            template = ZopeTwoPageTemplateFile('contract_nears_ending.pt')
            
            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=_(u'title_contract_near_ending',
                                         mapping={'name': employee.officialName()}))
            email.send()
            notify(ContractEndingEvent(employee))
            notified.add_notification(EXPIRY_NOTIFICATION)


def trial_period_ending_checker(object, event):
    """Check if the trial period of employees is almost ending.

    object is likely the portal, but try not to depend on that.
    """
    portal = getToolByName(object, 'portal_url').getPortalObject()
    panel = IHRMNotificationsPanelSchema(object)
    if not panel.trial_ending_notification:
        logger.info("Trial period ending notification is switched off.")
        return
    days_warning = panel.trial_ending_notification_period

    language_tool = getToolByName(portal, 'portal_languages')
    if language_tool:
        language = language_tool.getDefaultLanguage()
    else:
        language = 'en'

    toLocalizedTime = portal.restrictedTraverse('@@plone').toLocalizedTime


    employees = get_employees_for_checking(portal)
    for brain in employees:
        try:
            employee = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue
        contracts = employee.restrictedTraverse('@@contracts')
        current_contract = contracts.current_contract()
        info = dict(employee_name = employee.officialName(),
                    employee_url = employee.absolute_url())
        if current_contract is None:
            continue
        trial_period_end = contracts.trial_period_end()
        if trial_period_end is None:
            # for example when there is no trial period...
            continue
        now = DateTime()
        if now + days_warning >= trial_period_end:
            # Check if we have already warned about this.
            notified = INotified(current_contract)
            if notified.has_notification(TRIAL_PERIOD_ENDING_NOTIFICATION):
                continue

            link_text = translate(_hrm(u'title_go_to_employee',
                                       mapping = {'name': employee.Title()}),
                                  target_language = language)

            options = {'date': toLocalizedTime(trial_period_end),
                       'link_href': employee.absolute_url(),
                       'link_text': link_text}
            template = ZopeTwoPageTemplateFile('trial_nears_ending.pt')

            
            addresses = utils.email_adresses_of_local_managers(employee)
            recipients = (addresses['worklocation_managers'] +
                          addresses['hrm_managers'])
            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=_(u'title_trial_near_ending',
                                         mapping={'name': employee.officialName()}))
            email.send()


            notify(TrialPeriodEndingEvent(employee))
            notified.add_notification(TRIAL_PERIOD_ENDING_NOTIFICATION)
