from Testing import ZopeTestCase

from Products.PloneTestCase import PloneTestCase as PloneTestCase
from Products.PloneTestCase.layer import onsetup

from Products.CMFCore.utils import getToolByName
from Products.Five.testbrowser import Browser
from Products.Five import fiveconfigure, zcml

from quintagroup.pingtool import PingTool
from quintagroup.pingtool.config import *

PRODUCTS = [PROJECTNAME]

@onsetup
def setup_product():
    """Set up additional products and ZCML required to test this product.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for this package and its dependencies
    fiveconfigure.debug_mode = True
    import quintagroup.pingtool
    zcml.load_config('configure.zcml', quintagroup.pingtool)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ZopeTestCase.installPackage(PROJECTNAME)

# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

setup_product()
map(PloneTestCase.installProduct, ('XMLRPCMethod',))

PloneTestCase.setupPloneSite(products=PRODUCTS)


class TestCase(PloneTestCase.PloneTestCase):
    """Base class used for test cases
    """

class FunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """

    def afterSetUp(self):
        super(FunctionalTestCase, self).afterSetUp()

        self.browser = Browser()

        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])

        self.ptool = getToolByName(self.portal, 'portal_properties')
        self.pitool = getToolByName(self.ptool, 'portal_pingtool')
        self.site_props = self.ptool.site_properties

    def loginAsManager(self, user='root', pwd='secret'):
        """points the browser to the login screen and logs in as user root with Manager role."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()

