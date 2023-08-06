from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_paab_policy():
    """Set up the additional products required for the paab site policy
    """

    # Load the zcml configuration for the paab.policy package (following Aspeli #72)

    fiveconfigure.debug_mode = True
    import paab.policy
    zcml.load_config('configure.zcml', paab.policy)
    fiveconfigure.debug_mode = False

    ztc.installPackage('paab.policy')

setup_paab_policy()
ptc.setupPloneSite(products=['paab.policy'])

class PaabPolicyTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package.
    """
    
    
