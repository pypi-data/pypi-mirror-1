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
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from persistent import Persistent

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
# We take the title of the chosen template usually, but this can be
# overridden by specifically filling in a title.  But at least the
# title is now not required:
Contract_schema['title'].required = False
Contract_schema['title'].widget.visible = {'view': 'visible',
                                           'edit': 'invisible'}

class ContractHourSpread(Persistent):
    def __init__(self):
        # Mode can be manual, manual_oddeven or auto.
        self.mode = 'auto'

        # Number of hours worked by week.
        self.total_hours = 0

        # Stores the number of hours per day.
        # Each cell is referenced as week_type + '_' + day number.
        # For example, 'even_0' defines number of hours worked on
        # monday of even weeks. 'odd_3' defines number of jours
        # worked on thurday for odd weeks.
        self.hours = {}
        for week in ['odd', 'even']:
            for day in range(0, 7):
                self.hours[week + '_' + str(day)] = 0

    def update_from_form(self, form):
        """ Takes the form submitted with the contract viewlet and
        updates data.

        This method does not raise any error has the form should have been
        checked previously by the KSS action called when submitting
        the form.
        If problems are found, this method dies silently.
        """

        def quarter_round(f):
            """ Takes a float and returns it rounded to the quarter
                x.0, x.25, x.50, x.75
            """
            int_part = int(f)
            float_part = f - int_part
            
            for i in range(0, 5):
                if float_part > (0.25 * (i - 1)) and float_part < (0.25 * i):
                    float_part = i and 0.25 * (i - 1) or 0.0
                    break

            return int_part + float_part


        # First, we check that all necessary fields are here.
        fields = ['contract_form_workdays',
                  'contract_form_number_hours',
                  'contract_form_working_schedule']

        for week in ['odd', 'even']:
            for day in range(0, 7):
                fields. append('schedule_' + week + '_' + str(day))

        for field in fields:
            if not field in form:
                # Should not happen.
                return
            if not form[field]:
                form[field] = 0

        self.mode = form['contract_form_working_schedule']
        try:
            hours = float(form['contract_form_number_hours'])
            workdays = int(form['contract_form_workdays'])
        except:
            # Should not happen.
            return

        if self.mode == 'auto':
            for week in ['odd', 'even']:
                for day in range(0, workdays):
                    self.hours[week + '_' + str(day)] = \
                                    quarter_round(hours / workdays)
        elif self.mode == 'manual':
            for day in range(0, 7):
                self.hours['odd_' + str(day)] = float(form['schedule_odd_' + \
                                                           str(day)])
                self.hours['even_' + str(day)] = float(form['schedule_odd_' + \
                                                            str(day)])
        elif self.mode == 'manual_oddeven':
            for day in range(0, 7):
                self.hours['odd_' + str(day)] = float(form['schedule_odd_' + \
                                                           str(day)])
                self.hours['even_' + str(day)] = float(form['schedule_even_' + \
                                                            str(day)])

    def get_value_from_field(self, field):
        key = field.split('schedule_')[-1]
        if key in self.hours:
            return self.hours[key]

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
            items = [(item.id, item.Title()) for item
                     in tool.listTemplates('contract')]
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
            return 0
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

    security.declarePublic('hour_spread')
    @property
    def hour_spread(self):
        """ Returns the object ContractHourSpread linked to the contract.
        If the object do not exist yet, then it is created.
        """
        annotations = IAnnotations(self)
        ANNO_KEY = 'plonehrm.contract'

        metadata = annotations.get(ANNO_KEY, None)
        if metadata is None:
            annotations[ANNO_KEY] = PersistentDict()
            metadata = annotations[ANNO_KEY]

        if not 'hour_spread' in metadata:
            metadata['hour_spread'] = ContractHourSpread()

        return metadata['hour_spread']

    def getHoursPerWeek(self):
        """ Returns the number of hours worked each week.
        """
        # Check if the user has Arbo rights.
        membership = getToolByName(self, 'portal_membership')
        is_arbo =  membership.checkPermission('plonehrm: manage Arbo content',
                                              self)

        if not is_arbo:
            return self.getHours()

        odd_weeks = 0
        even_weeks = 0

        for hour in self.hour_spread.hours:
            if hour.startswith('odd'):
                odd_weeks += float(self.hour_spread.hours[hour])
            else:
                even_weeks += float(self.hour_spread.hours[hour])

        if odd_weeks == even_weeks:
            return str(int(odd_weeks))
        else:
            return str(int(odd_weeks)) + '/' + str(int(even_weeks))

    def is_contract(self):
        return True

registerType(Contract, config.PROJECTNAME)
