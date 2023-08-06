__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from Acquisition import aq_parent
from Products.Archetypes.atapi import registerType
from zope import component
from zope.interface import implements

from Products.plonehrm.interfaces import IEmployee
from plonehrm.contracts import config
from plonehrm.contracts.content.contract import Contract
from plonehrm.contracts.content.contract import Contract_schema
from plonehrm.contracts.interfaces import ILetter

Letter_schema = Contract_schema.copy()
Letter_schema['duration'].widget.visible={'view':'visible', 'edit':'invisible'}
Letter_schema['trialPeriod'].widget.visible={'view':'visible', 'edit':'invisible'}
Letter_schema['wage'].default_method='default_wage'
Letter_schema['function'].default_method='default_function'


class Letter(Contract):
    """Letter for change of contract
    """
    __implements__ = (getattr(Contract,'__implements__',()),)
    implements(ILetter)

    _at_rename_after_creation = True

    schema = Letter_schema

    def base_contract(self):
        """Get the current contract of the parent Employee.
        We may want to watch out for portal_factory though.
        """
        parent = aq_parent(self)
        if not IEmployee.providedBy(parent):
            return None

        # XXX: Remove view lookup
        # A content class should not need to be aware of the request in
        # order to preserve separation of concerns.  The subsitution
        # mechanism here should be replaced with a component that doesn't
        # know or care about the request - Rocky
        view = component.getMultiAdapter((parent, self.REQUEST),
                                         name=u'contracts')
        return view.current_contract()

    def default_wage(self):
        """Get the wage of the parent Employee.
        """
        base = self.base_contract()
        if base is None:
            return '0.00'
        return base.getWage()

    def default_function(self):
        """Get the function of the parent Employee.
        """
        base = self.base_contract()
        if base is None:
            return ''
        return base.getFunction()

registerType(Letter, config.PROJECTNAME)
