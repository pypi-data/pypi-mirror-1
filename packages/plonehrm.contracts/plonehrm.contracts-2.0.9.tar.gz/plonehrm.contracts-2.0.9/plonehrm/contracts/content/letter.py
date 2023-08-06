__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from Acquisition import aq_parent, aq_chain
from Products.Archetypes.atapi import registerType
from zope import component
from zope.interface import implements


from plonehrm.contracts import config
from plonehrm.contracts.content.contract import Contract
from plonehrm.contracts.content.contract import Contract_schema
from plonehrm.contracts.interfaces import ILetter

Letter_schema = Contract_schema.copy()
Letter_schema['duration'].widget.visible={'view':'visible', 'edit':'invisible'}
Letter_schema['trialPeriod'].widget.visible={'view':'visible', 'edit':'invisible'}


class Letter(Contract):
    """Letter for change of contract
    """
    __implements__ = (getattr(Contract,'__implements__',()),)
    implements(ILetter)

    _at_rename_after_creation = True

    schema = Letter_schema

registerType(Letter, config.PROJECTNAME)
