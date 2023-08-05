from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.CMFCore.utils import getToolByName
import plonehrm.contracts


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     plonehrm.contracts)
    fiveconfigure.debug_mode = False
    ztc.installPackage('plonehrm.contracts')


class BaseTestCase(ptc.PloneTestCase):
    """Base test case for.
    """

    def afterSetUp(self):
        # Products.plonehrm adds plonehrm.contracts to the Non
        # Installable Products so they do not clutter the QuickInstaller
        # interface.  We need to undo that here or work around it.
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        product = 'plonehrm.contracts'
        if not qi.isProductInstalled(product):
            qi.installProduct(product)


setup_product()
ptc.setupPloneSite(products=['plonehrm.contracts'])
