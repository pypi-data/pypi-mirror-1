from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.portlet.truereview
    zcml.load_config('configure.zcml', collective.portlet.truereview)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(products=['collective.portlet.truereview'])

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """