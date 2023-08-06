from zope.interface import Interface
from Products.Archetypes.atapi import Schema

class IGalleryType(Interface):
    
    def __init__(self, gallery=None):
        pass
    
    def schema(self):
        pass
        
    def name(self):
        pass
    
    def description(self):
        pass
        
    def images(self, gallery):
        pass
        
    def check_size(self):
        pass
        
    def validate(self, value, *args, **kwargs):
        pass

class IBaseGallery(Interface):
        
    def getImageUrl(self, image, subGallery=None):
        pass
        
    def getThumbUrl(self, image, subGallery=None):
        pass
        
    def getImageInfoDict(self, image):
        pass
    

class IGallery(Interface):
    """Gallery marker interface
    """
    def generateJavascript(self):
        pass

    def generateCSS(self):
        pass
    
    def containsSubGalleries(self):
        pass
        
    def getGalleryType(self):
        pass
    
class ISubGallery(IGallery):
    """Gallery marker interface
    """