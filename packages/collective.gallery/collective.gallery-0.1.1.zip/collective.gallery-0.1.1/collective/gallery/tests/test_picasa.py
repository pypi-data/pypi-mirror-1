import unittest
from collective.gallery.tests.base import GalleryTestCase

from Products.CMFCore.utils import getToolByName
from collective.gallery import picasa
class TestPicasaLink(GalleryTestCase):
    
    def afterSetUp(self):
        self.folder.invokeFactory('Link', "mylink")
        self.mylink = self.folder.mylink

    def beforeTearDown(self):
        pass

    def test_link_browserview(self):
        request = {}
        self.mylink.setRemoteUrl('http://www.nopicasa.fr/toto')
        self.assertRaises(Exception, picasa.Link, self.mylink, request)
        self.mylink.setRemoteUrl('http://picasaweb.google.fr/ceronjeanpierre/PhotosTriEsDuMariage')
        view = picasa.Link(self.mylink, request)
        
        #how can I test view.imgs ?

class TestPicasaSlideShow(GalleryTestCase):
    
    def test_slideShow(self):
        self.folder.invokeFactory('Link', "mylink")
        link = self.folder.mylink
        link.setRemoteUrl('http://picasaweb.google.fr/ceronjeanpierre/PhotosTriEsDuMariage')
        view = picasa.SlideShow(link, {})
        slideshow = view.slideshow()
        self.failUnless(slideshow.startswith("<embed"))
        self.failUnless("slideshow.swf" in slideshow)

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPicasaLink))
    suite.addTest(unittest.makeSuite(TestPicasaSlideShow))
    return suite
