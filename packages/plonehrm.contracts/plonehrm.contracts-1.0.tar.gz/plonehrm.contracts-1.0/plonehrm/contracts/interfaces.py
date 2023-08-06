from zope.interface import Interface


class IContract(Interface):

    def getId():
        """ """

    def setId():
        """ """

    def Title():
        """ """

    def Description():
        """ """

    def setDescription():
        """ """

    def getWage():
        """return the current wage"""

    def setWage():
        """set the current wage"""

    def getFunction():
        """Returns the function"""

    def setFunction():
        """Set the function"""

    def getStartdate():
        """Get the start date of the contract"""

    def setStartdate():
        """Set the start date of the contract"""

    def getDuration():
        """ """

    def setDuration():
        """ """

    def getEmploymentType():
        """ """

    def setEmploymentType():
        """ """

    def getHoures():
        """ """

    def setHours():
        """ """

    def getTemplate():
        """ """

    def setTemplate():
        """ """


class ILetter(IContract):
    """An official letter"""


class IContractTool(Interface):
    """Tool to manage templates, positions, and contract types."""
