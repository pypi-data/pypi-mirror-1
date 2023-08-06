import unittest
import time

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_package():
    """Set up the additional products required for the package.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    # Load the ZCML configuration for the package.
    # This includes the other products below as well.
    fiveconfigure.debug_mode = True
    import xm.hitcounter
    zcml.load_config('configure.zcml', xm.hitcounter)
    fiveconfigure.debug_mode = False
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    ztc.installProduct('Archetypes')
    ztc.installProduct('xm.hitcounter')
    ztc.installPackage('xm.hitcounter')

# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_package()

if 0: #use POI
    from Products.IOI.config import PRODUCT_DEPENDENCIES
    from Products.IOI.config import DEPENDENCIES

    # Add common dependencies
    DEPENDENCIES.append('Archetypes')
    PRODUCT_DEPENDENCIES.append('MimetypesRegistry')
    PRODUCT_DEPENDENCIES.append('PortalTransforms')
    PRODUCT_DEPENDENCIES.append('IOI')

    # Install all (product-) dependencies, install them too
    for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
        ZopeTestCase.installProduct(dependency)

    ZopeTestCase.installProduct('IOI')

    PRODUCTS = list()
    PRODUCTS += DEPENDENCIES
    PRODUCTS.append('IOI')

    ptc.setupPloneSite(products=['Archetypes',
                                 'ATVocabularyManager',
                                 'MimetypesRegistry',
                                 'PortalTransforms',
                                 'xm.fields',
                                 ]+PRODUCTS)

    ptc.installProduct('ATVocabularyManager')
else:
    
    ptc.setupPloneSite(products=['Archetypes','xm.hitcounter'])
import xm.hitcounter

class HitcounterTestCase(ptc.PloneTestCase):
    """ Base Test
    """

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='xm.hitcounter',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='xm.hitcounter.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='xm.hitcounter',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
           '_xm.hitcounder.test.txt', package='xm.hitcounter.doc',
           test_class=HitcounterTestCase),

        ])

if __name__ == '__main__':
    st = time.time()
    unittest.main(defaultTest='test_suite')
    tot = time.time()-st
    print "overall test time: %dm %02ds" % (int(tot) /60, tot%60) 
