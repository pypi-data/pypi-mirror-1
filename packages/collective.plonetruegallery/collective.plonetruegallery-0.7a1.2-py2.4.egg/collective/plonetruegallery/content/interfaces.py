from zope.interface import Interface
from Products.Archetypes.atapi import Schema

class IGallery(Interface):
    """Gallery marker interface
    """
    
    def containsSubGalleries(self):
        """"""
        
    def galleries(self):
        """"""