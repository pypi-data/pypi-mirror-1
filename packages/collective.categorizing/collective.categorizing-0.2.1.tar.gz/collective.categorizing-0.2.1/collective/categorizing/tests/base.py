from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_collective_categorizing():
    """Set up the additional products required for the Mall Content.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the collective.categorizing package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True
    import collective.categorizing
    zcml.load_config('configure.zcml', collective.categorizing)
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.categorizing')

# The order here is important: We first call the (deferred) function which
# installs the products we need for the Mall package. Then, we let 
# PloneTestCase set up this product on installation.

setup_collective_categorizing()
ptc.setupPloneSite(products=['collective.categorizing'])

class CollectiveCategorizingTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """

class CollectiveCategorizingFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
