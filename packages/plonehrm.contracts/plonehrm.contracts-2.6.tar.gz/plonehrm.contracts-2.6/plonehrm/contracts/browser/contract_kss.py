from Acquisition import aq_inner
from DateTime import DateTime
from kss.core import kssaction, KSSView
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate

from plonehrm.contracts import ContractsMessageFactory as _

class ContractKssView(KSSView):
    """ Class managing KSS actions for the contract viewlet.
    """

    def replace_viewlet(self, mode = 'list'):
        """ This method refreshes the content of the
        contract viewlet.
        The 'mode' parameter is used to know which type of view is
        used.
        """

        # We check that the mode used is a correct one.
        if not mode in ['list', 'add_contract', 'add_letter',
                        'settings', 'endEmployment']:
            mode = 'list'

        # First, we get the viewlet manager.
        view = self.context.restrictedTraverse('@@plonehrm.contracts')

        # We configure it.
        view.view_mode = mode

        # We get the content displayed by in the viewlet.
        rendered = view.render()

        # We replace the content of the viewlet by the new one.
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('plonehrmContractViewlet')
        core.replaceHTML(selector, rendered)

    @property
    def lang(self):
        props = getToolByName(self.context, 'portal_properties')
        return props.site_properties.getProperty('default_language')     

    @kssaction
    def show_list(self, hide_status=True):
        """ Shows the contract list in the viewlet.
        """
        
        #Hides the previous status message.
        if hide_status:
            self.getCommandSet('plone').issuePortalMessage('')

        self.replace_viewlet('list')

    @kssaction
    def show_add_letter(self):
        """ Shows the add letter form in the viewlet.
        """
        self.replace_viewlet('add_letter')

    @kssaction
    def show_add_contract(self):
        """ Shows the add letter form in the viewlet.
        """
        self.replace_viewlet('add_contract')

    @kssaction
    def show_settings(self):
        """ Shows the settings form in the viewlet.
        """
        self.replace_viewlet('settings')

    @kssaction
    def show_end_employment(self):
        """ Shows the form to end employment.
        """
        self.replace_viewlet('endEmployment')

    @kssaction
    def save_settings(self):
        """ Saves the settings for the employee.
        The form is not passed as a parameter, we use
        kssSubmitForm to send the data.
        """
        form = self.request.form
        core = self.getCommandSet('core')

        field_base = 'contract_settings_start_date'
        if form.get(field_base + '_year', '0000') != '0000':
            year = int(self.request.get(field_base + '_year'))
            month = int(self.request.get(field_base + '_month'))
            day = int(self.request.get(field_base + '_day'))
            try:
                date = DateTime(year, month, day)
            except:
                selector = core.getHtmlIdSelector(
                    'contract_viewlet_settings_baddate_error')
                core.setAttribute(selector, 'class', 'errormessage')

                # Show error status message
                message = translate(_(u'msg_error_saving_settings',
                                      u'Errors have been found when saving settings'),
                                    target_language=self.lang)
                self.getCommandSet('plone').issuePortalMessage(message,
                                                               msgtype='Error')
                
                return

            if date and not date.isPast():
                # Displays an error message
                selector = core.getHtmlIdSelector(
                    'contract_viewlet_settings_pastdate_error')
                core.setAttribute(selector, 'class', 'errormessage')

                message = translate(_(u'msg_error_saving_settings',
                                      u'Errors have been found when saving settings'),
                                    target_language=self.lang)
                self.getCommandSet('plone').issuePortalMessage(message,
                                                               msgtype='Error')
                return
        else:
            date = None

        # Save the date and display the contract list again.
        self.context.setWorkStartDate(date)

        if date is None:
            message = ''
        else:
            message = translate(_(u'msg_settings_savec',
                                  u'Settings have been saved'),
                                target_language=self.lang)

        self.getCommandSet('plone').issuePortalMessage(message)
        self.show_list(hide_status=False)

    @kssaction
    def end_employment(self):
        """ Sets date and reason for employment end.
        """
        form = self.request.form
        core = self.getCommandSet('core')

        employee = aq_inner(self.context)
        fields = ['end_employment_reason',
                  'contract_end_employment_date_day',
                  'contract_end_employment_date_month',
                  'contract_end_employment_date_year']

        for field in fields:
            if not field in form:
                # Should not happen.
                return

        # Hide previous errors.
        errors = ['contract_viewlet_end_date_invalid_error',
                  'contract_viewlet_end_date_empty_error']
        
        for error in errors:
            selector = core.getHtmlIdSelector(error)
            core.setAttribute(selector, 'class', 'dont-show')

        # Potential error message.
        message = translate(_(u'msg_employee_errors',
                              u'Errors have been found while terminating employment.'),
                            target_language=self.lang)

        # Check that a date has been set.
        if form['contract_end_employment_date_day'] == '00':
            selector = core.getHtmlIdSelector(
                'contract_viewlet_end_date_empty_error')
            core.setAttribute(selector, 'class', 'errormessage')
            self.getCommandSet('plone').issuePortalMessage(message,
                                                           msgtype='Error')
            return

        # Check that the date is correct.
        try:
            date = DateTime(int(form['contract_end_employment_date_year']),
                            int(form['contract_end_employment_date_month']),
                            int(form['contract_end_employment_date_day']))
        except:
            selector = core.getHtmlIdSelector(
                'contract_viewlet_end_date_invalid_error')
            core.setAttribute(selector, 'class', 'errormessage')
            self.getCommandSet('plone').issuePortalMessage(message,
                                                           msgtype='Error')
            return

        # Set end date/reason
        employee.setEndEmploymentDate(date)
        employee.setEndEmploymentReason(form['end_employment_reason'])

        # Change employee workflow.
        try:
            workflowTool = getToolByName(employee, "portal_workflow")
            workflowTool.doActionFor(employee, "deactivate")
        except:
            # The employment was already terminated.
            pass

        # Show the success message.
        message = translate(_(u'msg_employee_ended',
                              u'Employment has been terminated.'),
                            target_language=self.lang)

        self.getCommandSet('plone').issuePortalMessage(message)

        # Refresh the viewlet.
        self.show_list(hide_status=False)
        
        # Refresh the checklist viewlet.
        view = self.context.restrictedTraverse('@@plonehrm.checklist')

        # We configure it.
        view.view_mode = 'list'
        view.editedItem = None

        # We get the content displayed by in the viewlet.
        rendered = view.render()

        # We replace the content of the viewlet by the new one.
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('checklist')
        core.replaceHTML(selector, rendered)




    def _validate_field(self, value, errormsg, type='int', errors = []):
        """ This method tries to cast value into the asked type.
        If casting is not possible, the error message is appended into
        the errors list.
        """
        if value:
            try:
                if type == 'int':
                    int(value)
                elif type == 'float':
                    tmp = '.'.join(value.split(','))
                    float(tmp)
            except ValueError:
                errors.append(errormsg)

    @kssaction
    def add_contract(self):
        """ Method called when a new contract is added.
        """
        self.add_contract_or_letter()

    @kssaction
    def add_letter(self):
        """ Method called when a new letter is added.
        """
        self.add_contract_or_letter(False)

    def add_contract_or_letter(self, is_contract = True):
        """ Action called when a contract/letter is saved.
        """
        form = self.request.form
        core = self.getCommandSet('core')

        field_base = 'contract_form_'

        title = form.get(field_base + 'title')
        template = form.get(field_base + 'template')
        wage = form.get(field_base + 'wage')
        year = form.get(field_base + 'startdate_year')
        month = form.get(field_base + 'startdate_month')
        day = form.get(field_base + 'startdate_day')
        function = form.get(field_base + 'function')
        duration = form.get(field_base + 'duration')
        trial_period = form.get(field_base + 'trial_period')
        employment_type = form.get(field_base + 'employment_type')
        number_hours = form.get(field_base + 'number_hours')
        workdays = form.get(field_base + 'workdays')

        # Before displaying any error, we clean the previous ones.
        for errorMsg in ['contract_viewlet_no_template',
                         'contract_viewlet_wage_no_float',
                         'contract_viewlet_invalid_date',
                         'contract_viewlet_duration_no_integer',
                         'contract_viewlet_hours_no_integer',
                         'contract_viewlet_workdays_no_integer',
                         'contract_viewlet_incorrect_workdays',
                         'contract_viewlet_spread_to_high',
                         'contract_viewlet_more_than_24',
                         'contract_viewlet_invalid_hour_spread']:
            selector = core.getHtmlIdSelector(errorMsg)
            core.setAttribute(selector, 'class', 'dont-show')

        errors = []

        if template == '':
            errors.append('contract_viewlet_no_template')

        self._validate_field(wage, 'contract_viewlet_wage_no_float',
                             'float', errors)

        if form.get(field_base + 'startdate_year', '0000') != '0000':
            try:
                date = DateTime(int(year), int(month), int(day))
            except:
                errors.append('contract_viewlet_invalid_date')
                date = None
        else:
            date = None

        self._validate_field(
            duration, 'contract_viewlet_duration_no_integer',
            'int', errors)


        if is_contract:
            # This field is not present in
            # the letter form.

            # We do not raise any error as this case should not append,
            # the only values possible for this field are 0, 1 or 2.
            self._validate_field(trial_period, '', 'int', errors)


        self._validate_field(number_hours, 'contract_viewlet_hours_no_integer',
                         'int', errors)
        if not number_hours:
            number_hours = 0

        try:
            tmp = int(workdays)
            if tmp < 1 or tmp > 7:
                errors.append('contract_viewlet_incorrect_workdays')
        except:
            if workdays:
                errors.append('contract_viewlet_workdays_no_integer')

        # We check that number of hours specified is correct.
        if 'contract_form_working_schedule' in form:
            total = 0
            if form['contract_form_working_schedule'] == 'manual':
                rows = ['odd']
            elif form['contract_form_working_schedule'] == 'manual_oddeven':
                rows = ['odd', 'even']
            else:
                rows = []

            for row in rows:
                for day in range(0, 7):
                    field = 'schedule_' + row + '_' + str(day)

                    if field in form:
                        try:
                            field_value = float(form[field])
                        except ValueError:
                            errors.append(
                                'contract_viewlet_invalid_hour_spread')
                        total += field_value
                        if field_value > 24:
                            errors.append('contract_viewlet_more_than_24')

            if rows:
                total = total / len(rows)
                if total > int(number_hours):
                    errors.append('contract_viewlet_spread_to_high')

        # We display the error messages.
        for errorMsg in errors:
            selector = core.getHtmlIdSelector(errorMsg)
            core.setAttribute(selector, 'class', 'errormessage')

        if len(errors) > 0:
            if is_contract:
                message = translate(_(u'msg_error_contract',
                                      u'Errors were found while creating the contract'),
                                target_language=self.lang)
            else:
                message = translate(_(u'msg_error_letter',
                                      u'Errors were found while creating the letter'),
                                target_language=self.lang)
                
            self.getCommandSet('plone').issuePortalMessage(message,
                                                           msgtype='Error')
            
            return

        # If no error has been found, we create the contract and display
        # the contract list.
        if is_contract:
            new_id = self.context.generateUniqueId('Contract')
            self.context.invokeFactory("Contract", id=new_id,
                                       title='contract_tmp')
        else:
            new_id = self.context.generateUniqueId('Letter')
            self.context.invokeFactory("Letter", id=new_id,
                                       title='letter_tmp')

        contract = getattr(self.context, new_id)

        contract.setTitle(title)
        contract.setTemplate(template)
        contract.setWage(wage)
        contract.setFunction(function)
        contract.setEmploymentType(employment_type)
        contract.setHours(number_hours)
        contract.setDaysPerWeek(workdays)
        contract.setStartdate(date)
        contract.setDuration(duration)
            
        if is_contract:
            contract.setTrialPeriod(trial_period)

        contract.unmarkCreationFlag()
        contract._renameAfterCreation()
        notify(ObjectInitializedEvent(contract))

        # Adds informations for hours spread.
        if 'contract_form_working_schedule' in form:
            contract.hour_spread.update_from_form(form)

        # Shows status message
        if is_contract:
            message = translate(_(u'msg_contract_added',
                                  u'Contract added'),
                                target_language=self.lang)
        else:
            message = translate(_(u'msg_letter_added',
                                  u'Letter added'),
                                target_language=self.lang)
        self.getCommandSet('plone').issuePortalMessage(message)
     

        self.show_list(hide_status=False)

    @kssaction
    def change_schedule_table(self, value):
        """ Show or hide the schedule table.
        """

        if value == 'auto':
            css = 'dont-show'
        elif value in ['manual', 'manual_oddeven']:
            css = 'listing'
        else:
            return
        
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('contract_viewlet_manual_schedule')
        core.setAttribute(selector, 'class', css)

        if not value == 'auto':
            if value == 'manual':
                css = 'dont-show'
                first_row = _(u'label_normal', u'normal')
            else:
                css = ''
                first_row = _(u'label_odd', u'odd')
            
            # We hide the second row which is useless.
            selector = core.getHtmlIdSelector(
                'contract_viewlet_manual_schedule_even')
            core.setAttribute(selector, 'class', css)

            selector = core.getHtmlIdSelector(
                'contract_viewlet_manual_schedule_odd_first_row')
            core.replaceInnerHTML(selector,
                                  translate(first_row,
                                            target_language=self.lang))
