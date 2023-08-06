from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
# from Products.Five import zcml
from Products.Five import fiveconfigure

import ilrt.migrationtool

@onsetup
def setup_products():
    fiveconfigure.debug_mode = True
    fiveconfigure.debug_mode = False    
    ztc.installPackage('ilrt.migrationtool')


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

setup_products()
ptc.setupPloneSite(policy='ilrt.migrationtool:default',
                   products=['ilrt.migrationtool'])



