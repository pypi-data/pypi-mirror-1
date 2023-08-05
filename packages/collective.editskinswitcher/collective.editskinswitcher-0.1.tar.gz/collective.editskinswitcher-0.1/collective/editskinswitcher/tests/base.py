from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure

import collective.editskinswitcher

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     collective.editskinswitcher)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.editskinswitcher') 
    # We add an access rule in the installer, so we need SiteAccess
    # available in our test instance.
    ztc.installProduct('SiteAccess')

class BaseTestCase(ptc.PloneTestCase):
    """Base class for test cases.
    """

class BaseFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for test cases.
    """

setup_product()
ptc.setupPloneSite(products=['collective.editskinswitcher'])
