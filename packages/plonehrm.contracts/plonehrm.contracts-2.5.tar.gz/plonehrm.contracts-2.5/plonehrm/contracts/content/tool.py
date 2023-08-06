__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import ImmutableId
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

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
            label=_(u'contract_label_employmentTypes',
                    default=u'Types of employment'),
        )
    ),
),
)

ContractTool_schema = BaseFolderSchema.copy() + schema.copy()


class ContractTool(ImmutableId, BaseFolder):
    """Contract tool.

      >>> from plonehrm.contracts.content.tool import ContractTool
      >>> tool = ContractTool()
      >>> tool.Title()
      'Contract templates'

      >>> tool.at_post_edit_script()

    """

    id = 'portal_contracts'
    security = ClassSecurityInfo()
    __implements__ = (BaseFolder.__implements__, )
    implements(IContractTool)

    typeDescription = "ContractTool"
    typeDescMsgId = 'description_edit_contracttool'

    schema = ContractTool_schema

    def __init__(self, *args, **kwargs):
        self.setTitle(translate(_(u'title_portal_contracts',
                                  default=u'Contract templates')))

    def listTemplates(self, type=None):
        """List the templates in this tool.

        Optionally list the templates from a higher level
        portal_contracts tool as well.  This is done by trying to call
        getUseHigherLevelTemplates on the current tool.  This method
        is not available by default, but can be implemented by third
        party products.  Default is False.  If you always want this to
        be True, add a python script getUseHigherLevelTool in the
        portal_skins/custom folder that just returns True.

        We return full objects; returning just ids will fail as we
        then have no way of knowing in which portal_contracts that
        template id is.

        When specifying the parameter 'type' we return only templates
        of that type (presumably 'contract' or 'letter'), otherwise we
        return all.
        """
        templates = self.contentValues()

        try:
            recursive = self.getUseHigherLevelTool()
        except AttributeError:
            recursive = False

        if recursive:
            # Get our grand parent and ask him for a portal_contracts
            # tool.  Note that if we ask our parent, then a
            # getToolByName will return ourselves, which is not what
            # we want.
            grand_parent = aq_parent(aq_parent(aq_inner(self)))
            higher_tool = getToolByName(grand_parent, self.id, None)
            if higher_tool is not None:
                templates += higher_tool.listTemplates()


        # We filter the templates to keep only contract/letter templates.
        filtered = []
        for template in templates:
            try:
                template_type = template.getType()
            except:
                # An old template stays in the contract tool.
                continue
            if type is None or template_type == type:
                filtered.append(template)

        return filtered

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObjectSecurity')
    def reindexObjectSecurity(self, skip_self=False):
        pass


registerType(ContractTool, config.PROJECTNAME)
