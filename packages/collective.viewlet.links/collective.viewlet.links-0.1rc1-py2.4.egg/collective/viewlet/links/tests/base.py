import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
from Products.Five.testbrowser import Browser

import collective.viewlet.links

@onsetup
def setup_product():
    """Set up additional products and ZCML required to
    test this product.

    The @onsetup decorator causes the execution of this
    body to be deferred until the setup of the Plone site
    testing layer.
    """
    #Load the ZCML config for this package and it's
    #dependenceis
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.viewlet.links)
    fiveconfigure.debug_mode = False

    #We need to tell the testing framework that these
    #products should be available.  This can't happen until
    #after we have loaded the zcml.
    ztc.installPackage('collective.viewlet.links')

#The order here is important: We first call the deferred
#function and then let ptc install it during Plone site
#setup
setup_product()
ptc.setupPloneSite(products=['collective.viewlet.links'])

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    pass

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
    def makeBrowser(self):
        browser = Browser()
        browser.mech_browser.request = self.app.REQUEST

        #False shows all errors, True handles some
        browser.handleErrors = False

        return browser

