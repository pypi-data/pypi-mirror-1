
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    """Set up the package and its dependencies.
    """

    fiveconfigure.debug_mode = True
    import kupu.mashups
    zcml.load_config('configure.zcml', kupu.mashups)
    fiveconfigure.debug_mode = False

    ztc.installPackage('kupu.mashups')

setup_product()
ptc.setupPloneSite(products=['kupu.mashups'])

class MashupsTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit 
    test cases.
    """

class MashupsFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """