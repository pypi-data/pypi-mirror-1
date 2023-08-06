__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import UniqueObject
from zope.i18n import translate
from zope.interface import implements

from plonehrm.contracts import config
from plonehrm.contracts.interfaces import IContractTool
from plonehrm.contracts import ContractsMessageFactory as _

schema = Schema((
    LinesField(
        name='functions',
        widget=LinesField._properties['widget'](
            label=_(u'contract_label_functions', default=u'Positions'),
        )
    ),
    LinesField(
        name='employmentTypes',
        widget=LinesField._properties['widget'](
            label=_(u'contract_label_employmentTypes', default=u'Types of employment'),
        )
    ),
),
)

ContractTool_schema = BaseFolderSchema.copy() + schema.copy()


class ContractTool(UniqueObject, BaseFolder):
    """Contract tool.

      >>> from plonehrm.contracts.content.tool import ContractTool
      >>> tool = ContractTool()
      >>> tool.Title()
      'Contract templates'

      >>> tool.at_post_edit_script()

    """

    security = ClassSecurityInfo()
    __implements__ = (BaseFolder.__implements__,)
    implements(IContractTool)

    typeDescription = "ContractTool"
    typeDescMsgId = 'description_edit_contracttool'

    schema = ContractTool_schema

    def __init__(self):
        self.id = 'portal_contracts'
        self.setTitle(translate(_(u'title_portal_contracts', default=u'Contract templates')))
        self.unindexObject()

    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()


registerType(ContractTool, config.PROJECTNAME)
