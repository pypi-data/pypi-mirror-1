from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from collective.plonetruegallery.content.config import *

def beforeUninstall(self, cascade, product, reinstall):
    out = StringIO()
    
    if reinstall:
        pass
    
    return out.getvalue(), cascade

def afterInstall(self, reinstall=False, **kwargs):
    out = StringIO()
    
    #Do this, because the old way of choosing a gallery type is will cause new objects to fail
    if reinstall:
        def updateGallery(gallery):
            if gallery.getType() not in GALLERY_TYPES.keys():
                gallery.setType(DEFAULT_GALLERY_TYPE)
                
        galleries = [g.getObject() for g in self.queryCatalog({'portal_type': 'Gallery'})]
        for gallery in galleries:
            updateGallery(gallery)
            
        subgalleries = [g.getObject() for g in self.queryCatalog({'portal_type': 'SubGallery'})]
        for gallery in subgalleries:
            updateGallery(gallery)
            
    return out.getvalue()