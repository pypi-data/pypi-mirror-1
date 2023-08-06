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
    StringField(
        name="size",
        widget=SelectionWidget(
            label="Size"
        ),
        vocabulary=(
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large')
        ),
        default="medium",
        enforceVocabulary = True
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
        default=False
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
        name='fadeInDuration',
        widget=IntegerField._properties['widget'](
            label="Fade In Duration",
            description="The amount of time the fading effect should take in miliseconds."
        ),
        required=1,
        default=500
    ),
    IntegerField(
        name='fadeOutDuration',
        widget=IntegerField._properties['widget'](
            label="Fade out Duration",
            description="The amount of time the fading effect should take in miliseconds."
        ),
        required=1,
        default=500
    ),
    StringField(
        name="inTransition",
        widget=SelectionWidget(
            label="Transition",
            description="Select the transition you want to use when an image is being added."
        ),
        vocabulary=(
            ('fade', 'Fade'),
            ('slide', 'Slide'),
            ('show', 'Show')
        ),
        default="fade",
        enforceVocabulary = True
    ),
    StringField(
        name="outTransition",
        widget=SelectionWidget(
            label="Transition Out",
            description="Select the transition you want to use when an image is being removed."
        ),
        vocabulary=(
            ('fade', 'Fade'),
            ('slide', 'Slide'),
            ('show', 'Show')
        ),
        default="fade",
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
    
    def __init__(self, arg1):
        ATFolder.__init__(self, arg1)
        
    def containsSubGalleries(self):
        return self.contains_sub_gallery_objects
        
    def generateCSS(self):
        return """
    	.jcarousel-skin-truegallery .jcarousel-clip-horizontal {
            height: %spx;
        }
        .jcarousel-skin-truegallery .jcarousel-item {
            width: %spx;
            height: %spx;
        }
        """ % (
            self.getThumbnailHeight() + 10,
            self.getThumbnailWidth(),
            self.getThumbnailHeight()
        )
        
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
    
    def getWidth(self):
        return self.getGalleryType().sizes[self.getSize()]['width']
        
    def getHeight(self):
        return self.getGalleryType().sizes[self.getSize()]['height']
    
    def getThumbnailWidth(self):
        return self.getGalleryType().getThumbnailWidth()
        
    def getThumbnailHeight(self):
        return self.getGalleryType().getThumbnailHeight()
        
    def images(self):
        if not self.containsSubGalleries():
            return self.getGalleryType().images() 
        else:
            return []
    
    def getPage(self, page):
        if not self.containsSubGalleries():
            return self.getGalleryType().getPage(int(page))
        else:
            return []
    
    def galleries(self):
        return [g.getObject() for g in self.getFolderContents() if g.meta_type == "Gallery"]
    
    def getFirstImage(self):
        if self.containsSubGalleries():
            return self.galleries()[0].getFirstImage()
        else:
            return self.getGalleryType().getFirstImage()
    
    def info(self):
        return self.getGalleryType().info()
    
    def generateJavascript(self):
        return """
        jq(document).ready(function(){
            document.trueGallery = new TrueGallery(jq('div#plone-true-gallery'), {
                image_width: %i,
                image_height: %i,
                thumbnail_width: %i,
                thumbnail_height: %i,
                timed: %s,
                delay: %i,
                hideSpeed: %i,
                hideType: '%s',
                showSpeed: %i,
                showType: '%s',
                showInfo: %s,
                showCarousel: %s
            });
        });
        """ % (
            self.getWidth(),
            self.getHeight(),
            self.getThumbnailWidth(),
            self.getThumbnailHeight(),
            str(self.getIsTimed()).lower(),
            self.getDelay(),
            self.getFadeOutDuration(),
            self.getOutTransition(),
            self.getFadeInDuration(),
            self.getInTransition(),
            str(self.getShowInfopane()).lower(),
            str(self.getShowCarousel()).lower()
        )
        
        
registerATCT(Gallery, PROJECTNAME)