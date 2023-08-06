import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
import collective.viewlet.navbar
ptc.setupPloneSite(products=['collective.viewlet.navbar'])



class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.viewlet.navbar)
            fiveconfigure.debug_mode = False
	    ztc.installPackage('collective.viewlet.navbar')
	    
        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='collective.viewlet.navbar',
            test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
