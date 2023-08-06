from zope.interface import Interface
from Products.Archetypes.atapi import Schema

class IGalleryType(Interface):
    """
    All Gallery Types must adhere to this interface
    """
    def __init__(self, gallery=None):
        pass
    
    def getSchema(self):
        """
        any extra fields required--should be part of a new schemata
        """
        pass
        
    def name(self):
        pass
    
    def description(self):
        pass
        
    def images(self, gallery):
        pass
        
    def check_size(self):
        pass
    
    def getPage(self, page):
        pass
        
    def getThumbnailWidth(self):
        pass

    def getThumbnailHeight(self):
        pass
    
    def getPage(self, page):
        pass
        
    def getFirstImage(self):
        pass

class IGallery(Interface):
    """Gallery marker interface
    """
    def generateJavascript(self):
        pass
    
    def containsSubGalleries(self):
        pass
        
    def getGalleryType(self):
        pass
        
    def getPage(self):
        pass
    
    def getThumbnailWidth(self):
        pass
    
    def getThumbnailHeight(self):
        pass
        
    def getWidth(self):
        pass

    def getHeight(self):
        pass

    def getPage(self, page):
        pass
        
    def getFirstImage(self):
        pass
    
class IBasicGalleryTypeValidator(Interface):
        
    def canValidate(self, gallery):
        pass
        
    def __call__(self, value, **kwargs):
        pass