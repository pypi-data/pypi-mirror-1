import unittest
from collective.js.s3slider.tests import base

from Products.CMFCore.utils import getToolByName

class TestSetup(base.S3SliderTestCase):
    """The name of the class should be meaningful. This may be a class that
    tests the installation of a particular product.
    """
    
    def test_javascript(self):
        js = self.portal.portal_javascripts.getResourceIds()
        self.failUnless("++resource++s3Slider.js" in js)

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
