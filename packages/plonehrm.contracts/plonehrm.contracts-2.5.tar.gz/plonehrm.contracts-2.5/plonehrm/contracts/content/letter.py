__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from Acquisition import aq_parent, aq_chain
from Products.Archetypes.atapi import registerType
from zope import component
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.utils import getToolByName

from plonehrm.contracts import config
from plonehrm.contracts.content.contract import Contract
from plonehrm.contracts.content.contract import Contract_schema
from plonehrm.contracts.interfaces import ILetter

Letter_schema = Contract_schema.copy()
Letter_schema['trialPeriod'].widget.visible={'view':'visible', 'edit':'invisible'}


class Letter(Contract):
    """Letter for change of contract
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(Contract,'__implements__',()),)
    implements(ILetter)

    _at_rename_after_creation = True

    schema = Letter_schema

    security.declarePrivate('_templates')
    def _templates(self):
        """Vocabulary for the template field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            items = [(item.id, item.Title()) for item
                     in tool.listTemplates('letter')]
            return DisplayList(items)

    def is_contract(self):
        return False

registerType(Letter, config.PROJECTNAME)
