from zope.interface import Interface
from Products.Archetypes.atapi import Schema

class IGalleryType(Interface):
    """
    All Gallery Types must adhere to this interface
    """
    def __init__(self, gallery=None):
        pass
    
    def schema(self):
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
        """
        called when the gallery is added to or edited
        """
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
    
class IBasicGalleryTypeValidator(Interface):
        
    def canValidate(self, gallery):
        pass
        
    def __call__(self, value, **kwargs):
        pass