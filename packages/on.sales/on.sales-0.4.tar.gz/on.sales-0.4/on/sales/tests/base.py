from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_on_sales():
    """Set up the additional products required for the Content.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the on.sales package.
    
    fiveconfigure.debug_mode = True
    import on.sales
    zcml.load_config('configure.zcml', on.sales)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    ztc.installPackage('on.sales')
    
setup_on_sales()
ptc.setupPloneSite(products=['on.sales'])

class SalesTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
        
class SalesFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
