from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

ztc.installProduct('zgeo.plone.geographer')

@onsetup
def setup_plone_kml():
    """Set up the additional products required for the Pleiades site policy.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for the optilux.policy package.
    
    fiveconfigure.debug_mode = True
    import zgeo.plone.kml
    zcml.load_config('configure.zcml', zgeo.plone.kml)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    ztc.installPackage('zgeo.plone.kml')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Pleiades package. Then, we let 
# PloneTestCase set up this product on installation.

setup_plone_kml()
ptc.setupPloneSite(products=['zgeo.plone.geographer'])

class PloneKMLTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

class PloneKMLFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

    def afterSetUp(test):
        lpf = test.portal.portal_types['Topic']
        lpf_allow = lpf.global_allow
        lpf.global_allow = True
        lpf = test.portal.portal_types['Large Plone Folder']
        lpf_allow = lpf.global_allow
        lpf.global_allow = True
