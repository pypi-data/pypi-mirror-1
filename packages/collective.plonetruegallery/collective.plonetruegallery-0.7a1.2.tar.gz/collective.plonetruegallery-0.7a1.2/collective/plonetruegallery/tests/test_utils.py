from Products.PloneTestCase.PloneTestCase import PloneTestCase
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from cStringIO import StringIO
import zope.app.publisher.browser
from Products.Five.testbrowser import Browser
from base import PTGTestCase
from collective.plonetruegallery.content.config import PAGE_SIZE
from zope.publisher.browser import TestRequest

from collective.plonetruegallery.galleryadapters.basic import BasicAdapter
from collective.plonetruegallery.galleryadapters.flickr import FlickrAdapter
from collective.plonetruegallery.galleryadapters.picasa import PicasaAdapter
from collective.plonetruegallery.utils import getGalleryAdapter, getDisplayAdapter
from collective.plonetruegallery.browser.views.display import ClassicDisplayType, SlideshowDisplayType

def empty(self):
    pass

FlickrAdapter.cook = empty
PicasaAdapter.cook = empty

class TestUtils(PTGTestCase):
    """
    """

    def test_getGalleryAdapter_should_return_basic_adapter(self):
        gallery = self.portal['test_gallery']
        
        gallery.setType(BasicAdapter.name)
        
        adapter = getGalleryAdapter(gallery)
        
        self.failUnless(BasicAdapter == type(adapter))
        

    def test_getGalleryAdapter_should_return_flickr_adapter(self):
        gallery = self.portal['test_gallery']
        
        gallery.setType(FlickrAdapter.name)
        
        adapter = getGalleryAdapter(gallery)
        
        self.failUnless(FlickrAdapter == type(adapter))
        
    def test_getGalleryAdapter_should_return_picasa_adapter(self):
        gallery = self.portal['test_gallery']

        gallery.setType(PicasaAdapter.name)

        adapter = getGalleryAdapter(gallery)

        self.failUnless(PicasaAdapter == type(adapter))
        
    def test_getDisplayAdapter_should_return_classic_adapter(self):
        gallery = self.portal['test_gallery']

        gallery.setDisplayType(ClassicDisplayType.name)

        adapter = getDisplayAdapter(gallery, TestRequest())

        self.failUnless(ClassicDisplayType == type(adapter))
        
    def test_getDisplayAdapter_should_return_slideshow_adapter(self):
        gallery = self.portal['test_gallery']

        gallery.setDisplayType(SlideshowDisplayType.name)

        adapter = getDisplayAdapter(gallery, TestRequest())

        self.failUnless(SlideshowDisplayType == type(adapter))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    
    return suite