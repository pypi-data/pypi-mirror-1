import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

import collective.roundabout

from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    """Set up the package and its dependencies."""
    
    fiveconfigure.debug_mode = True
    import collective.roundabout
    zcml.load_config('configure.zcml', collective.roundabout)
    fiveconfigure.debug_mode = False

    ptc.installPackage('collective.roundabout')

setup_product()
ptc.setupPloneSite(extension_profiles=['collective.roundabout:default'])

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='collective.roundabout',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='collective.roundabout.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'README.txt', package='collective.roundabout',
            test_class=ptc.PloneTestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='collective.roundabout',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
