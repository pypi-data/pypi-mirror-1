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
        pass
            
    return out.getvalue()