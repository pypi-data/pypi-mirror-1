"""This is an integration "unit" test. It uses PloneTestCase, but does not
use doctest syntax.

You will find lots of examples of this type of test in CMFPlone/tests, for 
example.
"""

import unittest
from collective.gallery.tests.base import GalleryTestCase

from Products.CMFCore.utils import getToolByName

class TestSetup(GalleryTestCase):
    """The name of the class should be meaningful. This may be a class that
    tests the installation of a particular product.
    """
    
    def afterSetUp(self):
        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """
        self.portal_types = getToolByName(self.portal, 'portal_types')

    def beforeTearDown(self):
        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def test_link_view_methods(self):
        views = self.portal_types.getTypeInfo('Link').view_methods
        self.failUnless("s3slider" in views)
        self.failUnless("dewslider" in views)
        self.failUnless("picasa_slideshow" in views)

    def test_folder_view_methods(self):
        views = self.portal_types.getTypeInfo('Folder').view_methods
        self.failUnless("s3slider" in views)
        self.failUnless("dewslider" in views)

    def test_topic_view_methods(self):
        views = self.portal_types.getTypeInfo('Topic').view_methods
        self.failUnless("s3slider" in views)
        self.failUnless("dewslider" in views)

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
