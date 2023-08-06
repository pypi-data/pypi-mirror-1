from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure

import collective.editskinswitcher
from collective.editskinswitcher.tests.utils import new_default_skin


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     collective.editskinswitcher)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.editskinswitcher')


class BaseTestCase(ptc.PloneTestCase):
    """Base class for test cases.
    """

    def setUp(self):
        super(BaseTestCase, self).setUp()
        # Create new skin based on Plone Default and make this the
        # default skin.
        new_default_skin(self.portal)


class BaseFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for test cases.
    """

    def setUp(self):
        super(BaseFunctionalTestCase, self).setUp()
        # Create new skin based on Plone Default and make this the
        # default skin.
        new_default_skin(self.portal)


setup_product()
ptc.setupPloneSite(products=['collective.editskinswitcher'])
