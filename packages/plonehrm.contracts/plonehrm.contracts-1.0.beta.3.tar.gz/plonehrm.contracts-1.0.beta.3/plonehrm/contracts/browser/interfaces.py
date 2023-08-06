from zope.interface import Interface


class IContractView(Interface):
    """Provide a view for an Employee specifically for Contracts.
    """

    def current_contract():
        """Return a link to the contract"""

    def expires():
        """Return the expiration date of the current contract."""

    def trial_period_end():
        """Return the end of the trial period of the current contract."""


class IContractViewlet(Interface):

    def current_contract():
        """Return a link to the contract"""

    def expires():
        """Return the expiration date of the current contract."""

    def number():
        """Return the number of contracts.
        """

    def wage():
        """ Return the wage
        """

    def get_function():
        """ Return function
        """

    def add_url():
        """ Add new contract
        """

    def contract_list():
        """Return a list of contracts"""

    def sorted_contracts():
        """Return a sorted list of contracts and letters"""
