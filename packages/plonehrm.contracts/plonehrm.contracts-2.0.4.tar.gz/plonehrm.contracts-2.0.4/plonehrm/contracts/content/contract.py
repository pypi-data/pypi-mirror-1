__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain, aq_inner
from DateTime import DateTime
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
from Products.plonehrm.interfaces import IEmployee
from zope import component
from zope.interface import implements

from plonehrm.contracts import config
from plonehrm.contracts.interfaces import IContract
from plonehrm.contracts import ContractsMessageFactory as _

schema = Schema((
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
    FixedPointField(
        name='wage',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        validators = ('isCurrency', ),
        default_method='default_wage',
        widget=DecimalWidget(
            condition='not:object/template_chosen',
            label=_(u'contract_label_wage', default=u'Wage'),
        )
    ),
    StringField(
        name='function',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default_method='default_function',
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
        default_method='default_employment_type',
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
        default_method='default_hours',
        widget=IntegerWidget(
            condition='not:object/template_chosen',
            label=_(u'contract_label_hours', default=u'Number of hours'),
        )
    ),
    IntegerField(
        name='daysPerWeek',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default_method='default_days_per_week',
        validators = ('maxDaysPerWeek', ),
        widget=IntegerWidget(
            condition='not:object/template_chosen',
            label=_(u'contract_label_days_per_week',
                    default=u'Number of workdays per week'),
        )
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
Contract_schema['title'].widget.visible = {
    'view': 'visible', 'edit': 'invisible'}
Contract_schema['title'].required = False


class Contract(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseContent.__implements__, )
    implements(IBaseContent, IContract)
    _at_rename_after_creation = True

    schema = Contract_schema

    def getWage(self):
        """Override the default getting to return a comma in some cases.

        We just look at the default language and check if it is in a
        list of languages that we know use commas in their currencies.
        """
        wage = self.getField('wage').get(self)
        language_tool = getToolByName(self, 'portal_languages')
        if language_tool:
            language = language_tool.getDefaultLanguage()
        else:
            language = 'en'
        if language in ('nl', 'de', 'fr'):
            wage = wage.replace('.', ',')
        return wage

    security.declarePrivate('_templates')
    def _templates(self):
        """Vocabulary for the template field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            items = [(item.id, item.Title()) for item in tool.listTemplates()]
            return DisplayList(items)

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

    def get_employee(self):
        """Get the employee that this contract is in.

        Note that we probably are in the portal_factory, so our direct
        parent is not an Employee.  But we can traverse up the
        acquisition chain to find it.
        """
        for parent in aq_chain(aq_inner(self)):
            if IEmployee.providedBy(parent):
                return parent

    def base_contract(self):
        """Get the current contract of the parent Employee.
        """
        parent = self.get_employee()
        if parent is None:
            return
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
        if base is None or base == self:
            return '0.00'
        return base.getWage()

    def default_function(self):
        """Get the function of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return ''
        return base.getFunction()

    def default_hours(self):
        """Get the hours of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return ''
        return base.getHours()

    def default_employment_type(self):
        """Get the employment type of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return ''
        return base.getEmploymentType()

    def default_days_per_week(self):
        """Get the days per week of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return '0'
        return base.getDaysPerWeek()

    def expiry_date(self):
        """Expiry date of this contract.

        Basically start date + duration.  But e.g. a contract of one
        month starting at 31 January should end at 28 (or 29) February.

        Will return None if start date or duration is not known.
        """
        start = self.getStartdate()
        duration = self.getDuration()
        if start is None or duration is None:
            return None
        year, month, day = start.year(), start.month(), start.day()
        year = year + (month + duration - 1) / 12
        month = 1 + (month + duration - 1) % 12
        first_of_month = DateTime(year, month, 1)
        date = first_of_month + day - 1
        # 31 January + 31 days is 3 March, so count backwards in that
        # case.  Watch out for infinite loops here...
        safety_count = 5
        while date.month() != month and safety_count > 0:
            safety_count -= 1
            date -= 1
        if not safety_count:
            return None
        return date


registerType(Contract, config.PROJECTNAME)
