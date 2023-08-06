from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure

import collective.contentgenerator

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     collective.contentgenerator)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.contentgenerator')


class BaseTestCase(ptc.PloneTestCase):
    """Base class for test cases.
    """

    def setUp(self):
        super(BaseTestCase, self).setUp()

class BaseFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for test cases.
    """

    def setUp(self):
        super(BaseFunctionalTestCase, self).setUp()
        #self.portal

setup_product()
ptc.setupPloneSite(policy='collective.contentgenerator:default',products=['collective.contentgenerator'])
