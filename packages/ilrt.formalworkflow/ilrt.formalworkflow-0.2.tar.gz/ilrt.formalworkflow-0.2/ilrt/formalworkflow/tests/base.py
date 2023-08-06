from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure

import ilrt.formalworkflow
import plone.app.iterate

@onsetup
def setup_products():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     ilrt.formalworkflow)
    fiveconfigure.debug_mode = False    
    ztc.installPackage('ilrt.formalworkflow')


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
ptc.setupPloneSite(policy='ilrt.formalworkflow:default',
                   products=['ilrt.formalworkflow'])



