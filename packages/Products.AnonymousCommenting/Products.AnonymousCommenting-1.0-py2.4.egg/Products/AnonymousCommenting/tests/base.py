import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from transaction import commit


from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
import Products.AnonymousCommenting

# there is no install package in Zope 2.9
TEST_INSTALL =True
if not hasattr(ztc, 'installPackage'):
    TEST_INSTALL = False

ptc.setupPloneSite()

@onsetup
def setup_product():
    """Set up the additional products required for this package.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for dependent packages.
    
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.AnonymousCommenting)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    if TEST_INSTALL:
        ztc.installPackage('Products.AnonymousCommenting')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need.Then, we let PloneTestCase set up this 
# product on installation.

setup_product()
ptc.setupPloneSite(products=['Products.AnonymousCommenting'])

# Manually call initialize() so that the monkey patch gets installed
Products.AnonymousCommenting.initialize(ztc.app)

class AnonymousCommentingTestCase(ptc.PloneTestCase):
    pass
    
            
def test_suite():
    return unittest.TestSuite([
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
