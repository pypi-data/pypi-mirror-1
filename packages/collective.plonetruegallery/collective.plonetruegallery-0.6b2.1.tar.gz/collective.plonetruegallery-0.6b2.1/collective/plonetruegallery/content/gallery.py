from interfaces import IGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from config import *
from collective.plonetruegallery.utils import GalleryTypes

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
        vocabulary=GalleryTypesVocabulary(GalleryTypes),
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
    StringField(
        name="inTransition",
        widget=SelectionWidget(
            label="Fade In Transition",
            description="Select the transition you want to use when an image is being added."
        ),
        vocabulary=TRANSITIONS,
        default="fade",
        enforceVocabulary = True
    ),
    IntegerField(
        name='fadeOutDuration',
        widget=IntegerField._properties['widget'](
            label="Fade Out Duration",
            description="The amount of time the fading effect should take in miliseconds."
        ),
        required=1,
        default=500
    ),
    StringField(
        name="outTransition",
        widget=SelectionWidget(
            label="Fade Out Transition",
            description="Select the transition you want to use when an image is being removed."
        ),
        vocabulary=TRANSITIONS,
        default="fade",
        enforceVocabulary = True
    ),
),
)


GallerySchema = ATFolderSchema.copy() + schema.copy()

for ginfo in GalleryTypes:
    GallerySchema = GallerySchema.copy() + ginfo.schema.copy()

#remove extra schematas
for field in GallerySchema.fields():
    if field.schemata not in [ginfo.name for ginfo in GalleryTypes]:
        field.schemata = "metadata"

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
        
    def galleries(self):
        return [g.getObject() for g in self.getFolderContents() if g.meta_type == "Gallery"]
        

registerATCT(Gallery, PROJECTNAME)