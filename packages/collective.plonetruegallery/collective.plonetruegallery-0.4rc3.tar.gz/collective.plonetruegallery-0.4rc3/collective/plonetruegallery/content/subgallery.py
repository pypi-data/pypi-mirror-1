from interfaces import ISubGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from Acquisition import aq_parent
from gallery import Gallery, GallerySchema


class SubGallery(ATFolder, Gallery):
    """A folder which can contain other items."""

    schema = GallerySchema.copy()
    
    portal_type    = 'SubGallery'
    archetype_name = 'SubGallery'
    _atct_newTypeFor = {'portal_type' : 'CMF Folder', 'meta_type' : 'Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    __implements__ = (Gallery.__implements__,)
    
    implements(ISubGallery)

    security       = ClassSecurityInfo()
    
    error = False
    errorMsg = ""
    
    def containsSubGalleries(self):
        return False
        
    def generateCSS(self):
        return """
        #myGallery
    	{
    		width: %spx !important;
    		height: %spx !important;
    	}
        """ % (self.getWidth(), self.getHeight())
        
    def generateJavascript(self):
        return """
            function startGallery() {
        		var myGallery = new gallery($('myGallery'), {
        			timed: %s,
        			showCarousel: %s,
        			fadeDuration: %i,
        			delay: %i,
        			defaultTransition: "%s"
        		});
        	}
        	window.addEvent('domready', startGallery);

        """ % (
            str(self.getIsTimed()).lower(),
            str(self.getShowCarousel()).lower(),
            self.getFadeDuration(),
            self.getDelay(),
            self.getDefaultTransition()
        )

registerATCT(SubGallery, PROJECTNAME)