from zope.i18n import translate
from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from Products.CMFCore.utils import getToolByName

from plonehrm.contracts import ContractsMessageFactory as _
from plonehrm.contracts.notifications.interfaces import IContractEvent


class NoContractEvent(ObjectEvent):
    implements(IContractEvent)


class ContractEndingEvent(ObjectEvent):
    """Contract is almost ending.
    """
    implements(IContractEvent)

    # This needs to be handled by a (HRM) Manager, e.g. a checklist
    # item specifically for managers needs to be created.
    for_manager = True

    def __init__(self, *args, **kwargs):
        super(ContractEndingEvent, self).__init__(*args, **kwargs)
        create_url = self.object.absolute_url() + \
            '/createObject?type_name=Contract'
        contracts = self.object.restrictedTraverse('@@contracts')
        expires = contracts.expires()
        # Add a message to make a new contract, with the correct link.
        text = _('msg_make_new_contract', u"Make new contract")
        props = getToolByName(self.object, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')
        text = translate(text, target_language=lang)
        self.message = text
        self.link_url = create_url
        self.date = expires


class TrialPeriodEndingEvent(ObjectEvent):
    """Trial period is almost ending.
    """
    implements(IContractEvent)

    # This needs to be handled by a (HRM) Manager, e.g. a checklist
    # item specifically for managers needs to be created.
    for_manager = True

    def __init__(self, *args, **kwargs):
        super(TrialPeriodEndingEvent, self).__init__(*args, **kwargs)
        contracts = self.object.restrictedTraverse('@@contracts')
        trial_period_end = contracts.trial_period_end()
        # Add a warning message.
        toLocalizedTime = self.object.restrictedTraverse(
            '@@plone').toLocalizedTime
        trial_period_end = toLocalizedTime(trial_period_end)
        text = _(u"Trial period ends at ${date}.",
                 mapping=dict(date=trial_period_end))
        props = getToolByName(self.object, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')
        self.message = translate(text, target_language=lang)
