import logging

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.plonehrm import utils
from Products.plonehrm.controlpanel import IHRMNotificationsPanelSchema
from plonehrm.contracts import ContractsMessageFactory as _
from plonehrm.contracts.notifications.events import ContractEndingEvent
from plonehrm.contracts.notifications.events import TrialPeriodEndingEvent
from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.notifications.interfaces import INotified
from plonehrm.notifications.utils import get_employees_for_checking
from zope.event import notify

log = logging.getLogger("plonehrm.contracts:")

EXPIRY_NOTIFICATION = u"plonehrm.contracts: Expiry notification"
TRIAL_PERIOD_ENDING_NOTIFICATION = u"plonehrm.contracts: Trial period ending"


def contract_ending_checker(object, event):
    """Check if the current contract of employees is almost ending.

    object is likely the portal, but try not to depend on that.
    """
    portal = getToolByName(object, 'portal_url').getPortalObject()
    panel = IHRMNotificationsPanelSchema(object)
    if not panel.contract_expiry_notification:
        log.info("Contract ending notification is switched off.")
        return
    days_warning = panel.contract_expiry_notification_period

    employees = get_employees_for_checking(object)
    for brain in employees:
        employee = brain.getObject()
        contracts = employee.restrictedTraverse('@@contracts')
        current_contract = contracts.current_contract()
        info = dict(employee_name = employee.officialName(),
                    employee_url = employee.absolute_url())
        if current_contract is None:
            #email = HRMEmailer(employee)
            #email.template = ZopeTwoPageTemplateFile('no_current_contract.pt')
            #email.send()
            #notify(NoContractEvent(employee))
            continue
        expires = contracts.expires()
        if expires is None:
            continue
        now = DateTime()
        if now + days_warning >= expires:
            # Check if we have already warned about this.
            notified = INotified(current_contract)
            if notified.has_notification(EXPIRY_NOTIFICATION):
                continue
            info['days'] = days_warning
            options = dict(days=days_warning)
            template = ZopeTwoPageTemplateFile('contract_nears_ending.pt')
            addresses = utils.email_adresses_of_local_managers(employee)
            recipients = (addresses['worklocation_managers'] +
                          addresses['hrm_managers'])
            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=_(u'A contract nears ending'))
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
        log.info("Trial period ending notification is switched off.")
        return
    days_warning = panel.trial_ending_notification_period

    employees = get_employees_for_checking(portal)
    for brain in employees:
        employee = brain.getObject()
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
            notify(TrialPeriodEndingEvent(employee))
            notified.add_notification(TRIAL_PERIOD_ENDING_NOTIFICATION)
