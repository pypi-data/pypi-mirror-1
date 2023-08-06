from Products.PloneTestCase.PloneTestCase import PloneTestCase
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from cStringIO import StringIO
import zope.app.publisher.browser
from Products.Five.testbrowser import Browser
from base import PTGTestCase

from collective.plonetruegallery.galleryadapters.basic import BasicAdapter

from zope.event import notify

from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.Archetypes.interfaces import IObjectEditedEvent

class TestSubscribers(PTGTestCase):
    """
    """
    
    def test_gallery_contains_sub_gallery_objects_should_be_true(self):
        gallery = self.portal['test_gallery']
        
        self.failUnless(gallery.contains_sub_gallery_objects == False)
        
        gallery.invokeFactory(id="subgallery", type_name="Gallery")
        
        self.failUnless(gallery.contains_sub_gallery_objects == True)
        
    def test_gallery_contains_sub_gallery_objects_should_be_true(self):
        gallery = self.portal['test_gallery']

        self.failUnless(gallery.contains_sub_gallery_objects == False)
        gallery.invokeFactory(id="subgallery", type_name="Gallery")
        self.failUnless(gallery.contains_sub_gallery_objects == True)
        gallery.manage_delObjects(['subgallery'])
        
        self.failUnless(gallery.contains_sub_gallery_objects == False)
        


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubscribers))
    
    return suite