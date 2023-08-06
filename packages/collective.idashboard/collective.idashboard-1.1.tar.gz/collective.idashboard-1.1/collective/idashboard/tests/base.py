from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_idashboard():
    """ The @onsetup decorator causes the execution of this body to be deferred
        until the setup of the Plone site testing layer.
    """
    # Load the ZCML configuration for the slc.dublettefinder package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True
    import collective.idashboard
    zcml.load_config('configure.zcml', collective.idashboard)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    ztc.installPackage('collective.idashboard')
    
setup_idashboard()
ptc.setupPloneSite(products=['collective.idashboard'])

class iDashboardTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
        
class iDashboardFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """


