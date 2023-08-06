__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.utils import IntDisplayList
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import DecimalWidget
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import FixedPointField
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName
from zope import component
from zope.interface import implements

from plonehrm.contracts import config
from plonehrm.contracts.interfaces import IContract
from plonehrm.contracts import ContractsMessageFactory as _


schema = Schema((
    FixedPointField(
        name='wage',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=DecimalWidget(
            condition='not:object/template_chosen',
            label=_(u'contract_label_wage', default=u'Wage'),
        )
    ),
    StringField(
        name='function',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=SelectionWidget(
            format='select',
            condition='not:object/template_chosen',
            label=_(u'contract_label_function', default=u'Function'),
        ),
        vocabulary='_available_functions'
    ),
    DateTimeField(
        name='startdate',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=CalendarWidget(
            condition='not:object/template_chosen',
            show_hm=0,
            label=_(u'contract_label_startdate', default=u'Start date'),
        )
    ),
    IntegerField(
        name='duration',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=IntegerWidget(
            condition='not:object/template_chosen',
            label=_(u'contract_label_duration', default=u'Duration (months)'),
        )
    ),
    IntegerField(
        name='trialPeriod',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default=0,
        widget=SelectionWidget(
            format='select',
            condition='not:object/template_chosen',
            label=_(u'contract_label_trial_period',
                    default=u'Trial period (months)'),
        ),
        vocabulary='_trial_period_vocabulary',
    ),
    StringField(
        name='employmentType',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=SelectionWidget(
            condition='not:object/template_chosen',
            format='select',
            label=_(u'contract_label_employmentType',
                    default=u'Type of employment'),
        ),
        vocabulary='_available_employment_types'
    ),
    IntegerField(
        name='hours',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=IntegerWidget(
            condition='not:object/template_chosen',
            label=_(u'contract_label_hours', default=u'Number of hours'),
        )
    ),
    StringField(name='template',
        required=1,
        vocabulary='_templates',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=SelectionWidget(
            format='select',
            condition='not:object/template_chosen',
            label=_(u'contract_label_template', default=u'Template'),
        ),
    ),
    TextField(name='text',
        required=False,
        seachable=False,
        primary=True,
        default_output_type = 'text/x-html-safe',
        widget = RichWidget(
                description = '',
                label = _(u'label_body_text', default=u'Body Text'),
                rows = 25,
                visible = {'view': 'visible', 'edit': 'invisible'},
                condition='object/template_chosen',
        ),
    )
),
)

Contract_schema = BaseSchema.copy() + schema.copy()


class Contract(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseContent.__implements__, )
    implements(IBaseContent, IContract)
    _at_rename_after_creation = True

    schema = Contract_schema

    security.declarePrivate('_templates')
    def _templates(self):
        """Vocabulary for the template field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            items = [(item.id, item.Title()) for item in tool.contentValues()]
            return DisplayList(items)

    security.declarePrivate('setTemplate')
    def setTemplate(self, value):
        """When setting the template, we want to change the main text.

        Note: this *MUST* be the last parameter that is set, so it
        MUST be the last field that is visible on the form, else wage
        and function will not be set.
        """

        # XXX: Remove view lookup
        # A content class should not need to be aware of the request in
        # order to preserve separation of concerns.  The subsitution
        # mechanism here should be replaced with a component that doesn't
        # know or care about the request - Rocky
        view = component.queryMultiAdapter((self, self.REQUEST),
                                           name=u'substituter')
        if view is None:
            raise ValueError('Components are not properly configured, could '
                             'not find "substituter" view')

        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None or value not in tool.contentIds():
            # Hm, odd.
            return
        self.template = value

        # Get the text from the template
        template_text = tool[self.template].getText()

        template_text = view.substitute(template_text)
        self.setText(template_text)

    security.declarePublic('template_chosen')
    def template_chosen(self):
        """Determine if the template (a string) has been chosen yet.
        """
        return len(self.getTemplate()) > 0

    security.declarePrivate('_available_functions')
    def _available_functions(self):
        """Vocabulary for the functions field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            return tool.getFunctions()

    security.declarePrivate('_available_employment_types')
    def _available_employment_types(self):
        """Vocabulary for the employmentType field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            return tool.getEmploymentTypes()

    security.declarePrivate('_trial_period_vocabulary')
    def _trial_period_vocabulary(self):
        """Vocabulary for the trialPeriod field
        """
        return IntDisplayList([(0, '0'), (1, '1'), (2, '2')])


registerType(Contract, config.PROJECTNAME)
