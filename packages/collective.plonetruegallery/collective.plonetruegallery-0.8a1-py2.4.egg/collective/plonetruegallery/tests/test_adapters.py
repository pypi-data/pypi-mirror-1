from Products.PloneTestCase.PloneTestCase import PloneTestCase
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from cStringIO import StringIO
import zope.app.publisher.browser
from Products.Five.testbrowser import Browser
from base import PTGTestCase
from collective.plonetruegallery.config import PAGE_SIZE

from collective.plonetruegallery.galleryadapters.base import BaseAdapter
from collective.plonetruegallery.galleryadapters.basic import BasicAdapter
from collective.plonetruegallery.galleryadapters.flickr import FlickrAdapter
from collective.plonetruegallery.galleryadapters.picasa import PicasaAdapter

from collective.plonetruegallery.meta.zcml import GalleryTypes, DisplayTypes
from zope.component import getMultiAdapter, getAdapter
from collective.plonetruegallery.settings import GallerySettings
from zope.publisher.browser import TestRequest
from collective.plonetruegallery.interfaces import IGalleryAdapter, IDisplayType
from collective.plonetruegallery.meta.zcml import getAllDisplayTypes, getAllGalleryTypes
from collective.plonetruegallery.config import named_adapter_prefix

class TestRegistration(PTGTestCase):
    
    def test_gallerytypes_registered(self):
        gallerytypes = getAllGalleryTypes()
        
        for t in gallerytypes:
            adapter = getMultiAdapter(
                (self.portal['test_gallery'], TestRequest()), 
                name=named_adapter_prefix + t.name
            )
            self.failUnless(isinstance(adapter, t))
        
    def test_displaytypes_registered(self):
        displaytypes = getAllDisplayTypes()
        
        gadapter = getMultiAdapter(
            (self.portal['test_gallery'], TestRequest()), 
            name=named_adapter_prefix + "basic"
        )
        for t in displaytypes:
            adapter = getAdapter(gadapter, name=named_adapter_prefix + t.name)
            self.failUnless(isinstance(adapter, t))

            
class TestBasicAdapter(PTGTestCase):
    
    def get_basic_adapter(self):
        return getMultiAdapter(
            (self.portal['test_gallery'], TestRequest()), 
            name=named_adapter_prefix + 'basic'
        )
    
    def test_should_cook_images_on_invoking(self):
        adapter = self.get_basic_adapter()

        self.failUnless(len(adapter.cooked_images) == 20)
        self.failUnless(adapter.number_of_images == 20)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRegistration))
    suite.addTest(makeSuite(TestBasicAdapter))
    
    return suite