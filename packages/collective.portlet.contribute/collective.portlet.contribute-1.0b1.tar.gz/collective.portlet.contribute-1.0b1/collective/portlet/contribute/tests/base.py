from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.portlet.contribute
    zcml.load_config('configure.zcml', collective.portlet.contribute)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(products=['collective.portlet.contribute'])

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """