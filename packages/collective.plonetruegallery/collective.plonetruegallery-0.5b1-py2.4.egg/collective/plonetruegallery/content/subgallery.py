from interfaces import ISubGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from Acquisition import aq_parent

copied_fields = {}
copied_fields['title'] = ATFolderSchema['title'].copy()
copied_fields['title'].searchable = 1
copied_fields['title'].widget.label = "Gallery Name"

schema = Schema((

    copied_fields['title']
),
)

SubGallerySchema = ATFolderSchema.copy() + schema.copy()

class SubGallery(ATFolder):
    """A folder which can contain other items."""

    schema         =  SubGallerySchema

    portal_type    = 'SubGallery'
    archetype_name = 'SubGallery'
    _atct_newTypeFor = {'portal_type' : 'CMF Folder', 'meta_type' : 'Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    __implements__ = (ATFolder.__implements__,)
    
    implements(ISubGallery)

    # Enable marshalling via WebDAV/FTP/ExternalEditor.
    __dav_marshall__ = True

    security       = ClassSecurityInfo()

    def getGallery(self):
        return aq_parent(self)

    def containsSubGalleries(self):
        return False
        
    def generateCSS(self):
        self.getGallery().generateCSS()
        
    #These methods are used so we don't have to "wake up" the image objects
    def getImageUrl(self, image, subGallery=None):
        return "%s/%s/image_%s" % (self.absolute_url(), image.id, self.getGallery().image_size)
        
    def getThumbUrl(self, image, subGallery=None):
        return "%s/%s/image_thumb" % (self.absolute_url(), image.id)
        
    def getGalleryType(self):
        return "gallery"
        
    def generateJavascript(self):
        return """
            function startGallery() {
        		var myGallery = new %s($('myGallery'), {
        			timed: %s,
        			showCarousel: %s,
        			fadeDuration: %i,
        			delay: %i,
        			defaultTransition: "%s"
        		});
        	}
        	window.addEvent('domready', startGallery);

        """ % (
            self.getGalleryType(),
            str(self.getGallery().getIsTimed()).lower(),
            str(self.getGallery().getShowCarousel()).lower(),
            self.getGallery().getFadeDuration(),
            self.getGallery().getDelay(),
            self.getGallery().getDefaultTransition()
        )

registerATCT(SubGallery, PROJECTNAME)