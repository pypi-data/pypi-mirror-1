from Acquisition import Explicit
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet


def compare_dates(a, b):
    return cmp(a.getStartdate(), b.getStartdate())


def sort_contracts(contracts):
    """Sort Contracts and Letters.

    This is a helper method that is easier to test (and write).

    Wanted:

    - future contract
    - current contract
      - second change to current contract
      - first change to current contract
    - previous contract
      - only change to previous contract

    Well, the indentation will be done with css or something, but the
    above order should be there.

    Make mock classes:

    >>> class MockContract(object):
    ...     portal_type = 'Contract'
    ...     def __init__(self, date):
    ...         self.date = date
    ...     def getStartdate(self):
    ...         return self.date
    ...     def __repr__(self):
    ...         return '%s from %r' % (self.portal_type, str(self.date))
    >>> class MockLetter(MockContract):
    ...     portal_type = 'Letter'

    Make sample objects.  Most in the past and one in the future:

    >>> contract_0 = MockContract(DateTime(1999, 1, 1))
    >>> letter_0 = MockLetter(DateTime(1999, 5, 16))
    >>> contract_1 = MockContract(DateTime(2001, 1, 1))
    >>> letter_1 = MockLetter(DateTime(2001, 5, 16))
    >>> contract_2 = MockContract(DateTime(2001, 7, 1))
    >>> letter_2a = MockLetter(DateTime(2001, 8, 16))
    >>> letter_2b = MockLetter(DateTime(2001, 10, 16))
    >>> contract_3 = MockContract(DateTime(2100, 1, 1))

    Now some easy tests:

    >>> sort_contracts([])
    []
    >>> sort_contracts([contract_1])
    [Contract from '2001/01/01']
    >>> sort_contracts([letter_1])
    [Letter from '2001/05/16']

    Contracts should be listed newest first.

    >>> sort_contracts([contract_3, contract_1, contract_2]) == [contract_3, contract_2, contract_1]
    True

    Same for letters:

    >>> sort_contracts([letter_2a, letter_1, letter_2b]) == [letter_2b, letter_2a, letter_1]
    True

    A change letter should be listed *after* its contract.

    >>> sort_contracts([letter_1, contract_1])
    [Contract from '2001/01/01', Letter from '2001/05/16']
    >>> sort_contracts([letter_2a, contract_2, letter_2b])
    [Contract from '2001/07/01', Letter from '2001/10/16', Letter from '2001/08/16']

    Now the middle ones.

    >>> contracts = [contract_1, contract_2, letter_1, letter_2a, letter_2b]
    >>> sort_contracts(contracts)
    [Contract from '2001/07/01', Letter from '2001/10/16', Letter from '2001/08/16', Contract from '2001/01/01', Letter from '2001/05/16']

    Add the last one.

    >>> contracts.append(contract_3)
    >>> sort_contracts(contracts)
    [Contract from '2100/01/01', Contract from '2001/07/01', Letter from '2001/10/16', Letter from '2001/08/16', Contract from '2001/01/01', Letter from '2001/05/16']

    See if adding Contract zero is for some reason difficult.

    >>> sort_contracts(contracts + [contract_0])
    [Contract from '2100/01/01', Contract from '2001/07/01', Letter from '2001/10/16', Letter from '2001/08/16', Contract from '2001/01/01', Letter from '2001/05/16', Contract from '1999/01/01']

    Check if starting with a Letter adds difficulties (thought doing
    so would be strange.

    >>> sort_contracts(contracts + [letter_0])
    [Contract from '2100/01/01', Contract from '2001/07/01', Letter from '2001/10/16', Letter from '2001/08/16', Contract from '2001/01/01', Letter from '2001/05/16', Letter from '1999/05/16']

    """
    contracts.sort(cmp=compare_dates, reverse=True)
    sorted = []
    changes = []
    for con in contracts:
        if con.portal_type == 'Contract':
            # First add the contract,
            sorted.append(con)
            # then add the temporary list of change letters,
            sorted += changes
            # then empty that listit
            changes = []
        else:
            changes.append(con)
    # For safety (and testing)
    sorted += changes
    return sorted


class ContractView(BrowserView):

    def first_contract(self):
        today = DateTime()
        filter = dict(portal_type='Contract')
        contracts = self.context.contentValues(filter=filter)
        if len(contracts) == 0:
            return None
        contracts.sort(cmp=compare_dates)
        return contracts[0]
        
    def start_employment(self):
        contract = self.first_contract()
        if contract is not None:
            start = contract.getStartdate()
            return start
        return None
        
    def sum_worktime(self):
        
        start_date = self.context.workStartDate
        if start_date is not None:
           worktime = start_date
        else:
           worktime = self.start_employment()
    
        if worktime is not None:
            today = DateTime()            
            expire = self.expires()          
            if expire is not None and expire < today:
                date_to_compare = expire
            else: 
                date_to_compare = today
            
            worktime_year = date_to_compare.year() - worktime.year() 
            worktime_month = date_to_compare.month() - worktime.month()
            
            if worktime_month < 0:
                worktime_month = worktime_month+12
                worktime_year = worktime_year-1
          
            return {'year': worktime_year,
                    'month': worktime_month}
            
        return None
        

    def current_contract(self, includeChangeLetters=True):
        """Return a link to the contract"""
        today = DateTime()
        # Get a list of contracts with start dates before today.
        if includeChangeLetters:
            filter=dict(portal_type=('Contract', 'Letter'))
        else:
            filter=dict(portal_type='Contract')
        contracts = self.context.contentValues(filter=filter)
        candidates = [(c.getStartdate(), c) for c in contracts
                      if today > c.getStartdate() > 0]
        if len(candidates) > 0:
            # sort by date
            candidates.sort()
            dummy, contract = candidates[-1]
            return contract
        return None

    def expires(self):
        """Return the expiration date of the current contract.

        ChangeLetters can have no duration as they cannot change the
        duration of the Contract they are changing.  So ignore those.

        XXX If the current contract almost expires and there already
        is a new contract, then we should probably take that date as
        expiry date.
        """
        contract = self.current_contract(includeChangeLetters=False)
        if contract is not None:
            start = contract.getStartdate()
            duration = contract.getDuration()
            if start is None or duration is None:
                return None
            year, month, day = start.year(), start.month(), start.day()
            year = year + (month + duration - 1) / 12
            month = 1 + (month + duration - 1) % 12
            # Try not to return e.g. 31 February ...
            first_of_month =  DateTime(year, month, 1)
            return first_of_month + day - 1
        return None
    
 
        
    def trial_period_end(self):
        """Return the expiration date of the current contract.

        ChangeLetters can have no duration as they cannot change the
        duration of the Contract they are changing.  So ignore those.

        XXX If the current contract almost expires and there already
        is a new contract, then we should probably take that date as
        expiry date.
        """
        contract = self.current_contract(includeChangeLetters=False)
        if contract is not None:
            start = contract.getStartdate()
            trialPeriod = contract.getTrialPeriod()
            if start is None or trialPeriod == 0:
                return None
            year, month, day = start.year(), start.month(), start.day()
            year = year + (month + trialPeriod - 1) / 12
            month = 1 + (month + trialPeriod - 1) % 12
            # Try not to return e.g. 31 February ...
            first_of_month =  DateTime(year, month, 1)
            return first_of_month + day - 1
        return None


class ContractViewlet(Explicit, ContractView):
    implements(IViewlet)
    render = ViewPageTemplateFile('contract.pt')

    def __init__(self, context, request, view, manager):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass

    def number(self):
        """Return the number of contracts.
        """
        cat = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brains = cat.searchResults({'portal_type': 'Contract', 'path': path})
        if brains:
            return len(brains)

    def wage(self):
        """ Return the wage
        """
        if self.current_contract():
            return self.current_contract().getWage()

    def get_function(self):
        """ Return function
        """

        if self.current_contract():
            return self.current_contract().getFunction()

    def add_url(self):
        """ Add new contract
        """
        # check Add permission on employee
        # return None if we don't have permission
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission('plonehrm: Add contract', self.context):
            url = self.context.absolute_url() + '/createObject?type_name=Contract'
            return url

    def contract_list(self):
        return self.context.contentValues(
            filter=dict(portal_type=('Contract', 'Letter')))

    def sorted_contracts(self):
        """Sort contracts and letters
        """
        candidates = sort_contracts(self.contract_list())
        results = []
        if len(candidates) > 0:
            for contract in candidates:
                con = dict(contract=contract,
                           typ=contract.portal_type.lower())
                results.append(con)
        return results
