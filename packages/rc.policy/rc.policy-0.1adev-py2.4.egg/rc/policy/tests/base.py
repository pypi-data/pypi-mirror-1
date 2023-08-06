from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_rc_policy():

    fiveconfigure.debug_mode = True
    import rc.policy
    zcml.load_config('configure.zcml', rc.policy)
    fiveconfigure.debug_mode = False

    ztc.installPackage('rc.policy')

setup_rc_policy()
ptc.setupPloneSite(products=['rc.policy'])

class RcPolicyTestCase(ptc.PloneTestCase):
    """This base class is used for all tests in this package.
    Utility or setup code can be added if necessary.
    """

