from DateTime import DateTime
from kss.core import kssaction, KSSView
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent


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
        if not mode in ['list', 'add_contract', 'add_letter', 'settings']:
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

    @kssaction
    def show_list(self):
        """ Shows the contract list in the viewlet.
        """
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
                return

            if date and not date.isPast():
                # Displays an error message
                selector = core.getHtmlIdSelector(
                    'contract_viewlet_settings_pastdate_error')
                core.setAttribute(selector, 'class', 'errormessage')
                return
        else:
            date = None

        # Save the date and display the contract list again.
        self.context.setWorkStartDate(date)
        self.show_list()

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
                         'contract_viewlet_incorrect_workdays']:
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

        if is_contract:
            # Those two fields are not present in
            # the letter form.
            self._validate_field(
                duration, 'contract_viewlet_duration_no_integer',
                'int', errors)

            # We do not raise any error as this case should not append,
            # the only values possible for this field are 0, 1 or 2.
            self._validate_field(trial_period, '', 'int', errors)


        self._validate_field(number_hours, 'contract_viewlet_hours_no_integer',
                         'int', errors)

        try:
            tmp = int(workdays)
            if tmp < 1 or tmp > 7:
                errors.append('contract_viewlet_incorrect_workdays')
        except:
            if workdays:
                errors.append('contract_viewlet_workdays_no_integer')

        # We display the error messages.
        for errorMsg in errors:
            selector = core.getHtmlIdSelector(errorMsg)
            core.setAttribute(selector, 'class', 'errormessage')

        if len(errors) > 0:
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

        if is_contract:
            contract.setDuration(duration)
            contract.setTrialPeriod(trial_period)

        contract.unmarkCreationFlag()
        contract._renameAfterCreation()
        notify(ObjectInitializedEvent(contract))

        self.show_list()
