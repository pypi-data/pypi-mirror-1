from Products.PloneTestCase.PloneTestCase import PloneTestCase
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from cStringIO import StringIO
import zope.app.publisher.browser
from Products.Five.testbrowser import Browser
from base import PTGTestCase
from collective.plonetruegallery.content.config import PAGE_SIZE

from collective.plonetruegallery.galleryadapters.base import BaseAdapter
from collective.plonetruegallery.galleryadapters.basic import BasicAdapter
from collective.plonetruegallery.galleryadapters.flickr import FlickrAdapter
from collective.plonetruegallery.galleryadapters.picasa import PicasaAdapter

class TestBaseAdapter(PTGTestCase):
    """
    """
    
    def get_base_adapter(self):
        return BaseAdapter(self.portal['test_gallery'])
        

            
class TestBasicAdapter(PTGTestCase):
    
    def get_basic_adapter(self):
        return BasicAdapter(self.portal['test_gallery'])
        
    def test_image_information_sould_be_correct(self):
        adapter = self.get_basic_adapter()
        image = adapter.gallery['1']
        
        info = adapter.assemble_image_information(image)
        
        self.failUnless(info['image_url'] == adapter.gallery.absolute_url() + "/1/image_preview")
        self.failUnless(info['thumb_url'] == adapter.gallery.absolute_url() + "/1/image_tile")
        self.failUnless(info['link'] == adapter.gallery.absolute_url() + "/1")
        self.failUnless(info['title'] == "Title for 1")
        self.failUnless(info['description'] == "Description for 1")
    
    def test_should_cook_images_on_invoking(self):
        adapter = self.get_basic_adapter()

        self.failUnless(len(adapter.get_all_cooked_images()) == 20)
        self.failUnless(adapter.number_of_images() == 20)

    def test_get_page_should_return_correct_amount_of_images(self):
        adapter = self.get_basic_adapter()

        self.failUnless(len(adapter.get_page(0)) == PAGE_SIZE)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBaseAdapter))
    suite.addTest(makeSuite(TestBasicAdapter))
    
    return suite