from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.portlet.workflowsteps
    zcml.load_config('configure.zcml', collective.portlet.workflowsteps)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(products=['collective.portlet.workflowsteps'])

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """