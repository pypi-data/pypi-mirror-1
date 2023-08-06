from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_theme_tests():
    """
    """
    
    fiveconfigure.debug_mode = True
    import plonetheme.terrafirma
    zcml.load_config('configure.zcml', plonetheme.terrafirma)
    fiveconfigure.debug_mode = False
    
    ztc.installPackage('plonetheme.terrafirma')
    
setup_theme_tests()
ptc.setupPloneSite(products=['plonetheme.terrafirma'])

class TerrafirmaTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
        
class TerrafirmaFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """