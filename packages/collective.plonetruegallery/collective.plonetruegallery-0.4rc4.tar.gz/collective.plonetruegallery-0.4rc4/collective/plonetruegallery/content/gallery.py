from interfaces import IGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from config import *

copied_fields = {}
copied_fields['title'] = ATFolderSchema['title'].copy()
copied_fields['title'].widget.label = "Gallery Name"

schema = Schema((

    copied_fields['title'],

    StringField(
        name="type",
        widget=SelectionWidget(
            label="Type",
            description="Select the type of gallery you want this to be.  If you select something other than default, you must fill out the information in the corresponding tab for that gallery type."
        ),
        vocabulary=GalleryTypesVocabulary(),
        default=DEFAULT_GALLERY_TYPE,
        enforceVocabulary = True,
        required=True
    ),

    IntegerField(
        name='width',
        widget=IntegerField._properties['widget'](
            label="Width",
            description="Width of the slideshow area in pixels."
        ),
        required=1,
        default=500
    ),
    IntegerField(
        name='height',
        widget=IntegerField._properties['widget'](
            label="Height",
            description="Height of the slideshow area in pixels."
        ),
        required=1,
        default=500
    ),
    BooleanField(
        name="showCarousel",
        widget=BooleanField._properties['widget'](
            label="Show Carousel?"
        ),
        default=True
    ),
    BooleanField(
        name="showInfopane",
        widget=BooleanField._properties['widget'](
            label="Show Info pane?"
        ),
        default=True
    ),
    BooleanField(
        name="isTimed",
        widget=BooleanField._properties['widget'](
            label="Timed?",
            description="Should this gallery automatically change images for the user?"
        ),
        default=True
    ),
    IntegerField(
        name='delay',
        widget=IntegerField._properties['widget'](
            label="Delay",
            description="If slide show is timed, the delay sets how long before the next image is shown in miliseconds."
        ),
        required=1,
        default=5000
    ),
    IntegerField(
        name='fadeDuration',
        widget=IntegerField._properties['widget'](
            label="Fade Duration",
            description="The amount of time the fading effect should take in miliseconds."
        ),
        required=1,
        default=500
    ),
    StringField(
        name="defaultTransition",
        widget=SelectionWidget(
            label="Transition",
            description="Select the transition you want to use when moving from image to image."
        ),
        vocabulary=(
            ('fade', 'Fade'),
            ('crossfade', 'Cross Fade'),
            ('fadebg', 'Fade Background'),
            ('fadeslideleft', 'Slide'),
            ('continuoushorizontal', 'Move Horizontally'),
            ('continuousvertical', "Move Vertically")
        ),
        default="crossfade",
        enforceVocabulary = True
    ),
),
)

GallerySchema = ATFolderSchema.copy() + schema.copy()

for name, gallery_type in GALLERY_TYPES.items():
    GallerySchema = GallerySchema + gallery_type().getSchema()

#remove extra schematas
for field in GallerySchema.fields():
    if field.schemata not in [gallery_type().name() for gallery_name, gallery_type in GALLERY_TYPES.items()]:
        field.schemata = "extra"

class Gallery(ATFolder):
    """A folder which can contain other items."""

    schema         =  GallerySchema

    portal_type    = 'Gallery'
    archetype_name = 'Gallery'
    _atct_newTypeFor = {'portal_type' : 'CMF Folder', 'meta_type' : 'Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()
    
    #will be set on creation
    image_size = "mini"

    __implements__ = (ATFolder.__implements__,)
    
    implements(IGallery)

    security       = ClassSecurityInfo()
    contains_sub_gallery_objects = False
    
    error = False
    errorMsg = ""
    
    def __init__(self, arg1):
        ATFolder.__init__(self, arg1)
        
    def containsSubGalleries(self):
        return self.contains_sub_gallery_objects
        
    def generateCSS(self):
        return """
        #myGallery
    	{
    		width: %spx !important;
    		height: %spx !important;
    	}
        """ % (self.getWidth(), self.getHeight())
        
    def getGallerySmoothType(self):
        if self.containsSubGalleries():
            return "gallerySet"
        else:
            return "gallery"
        
    def getGalleryType(self, index=None):
        
        if index is None:
            index = self.getType()
            
        if index in GALLERY_TYPES.keys():
            t = GALLERY_TYPES[index]
            return t(self)
        #always default to basic gallery
        else:
            t = GALLERY_TYPES[DEFAULT_GALLERY_TYPE]
            return t(self)
        
    def images(self):
        return self.getGalleryType().images()
        
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
            self.getGallerySmoothType(),
            str(self.getIsTimed()).lower(),
            str(self.getShowCarousel()).lower(),
            self.getFadeDuration(),
            self.getDelay(),
            self.getDefaultTransition()
        )
        
        
registerATCT(Gallery, PROJECTNAME)