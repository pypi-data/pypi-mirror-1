from interfaces import IGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from config import *
from collective.plonetruegallery.utils import GalleryTypes, PTGMessageFactory as _

copied_fields = {}
copied_fields['title'] = ATFolderSchema['title'].copy()
copied_fields['title'].widget.label = _(u"label_gallery_name", default=u"Gallery Name")

schema = Schema((

    copied_fields['title'],

    StringField(
        name="type",
        widget=SelectionWidget(
            label=_(u"label_gallery_type", default=u"Type"),
            description=_(u"description_gallery_type", 
                default=u"Select the type of gallery you want this to be.  "
                        u"If you select something other than default, you "
                        u"must fill out the information in the corresponding tab for that gallery type.")
        ),
        vocabulary=GalleryTypesVocabulary(GalleryTypes),
        default=DEFAULT_GALLERY_TYPE,
        enforceVocabulary = True,
        required=True
    ),
    StringField(
        name="size",
        widget=SelectionWidget(
            label=_(u"label_gallery_size", default=u"Size")
        ),
        vocabulary=(
            ('small', _(u"label_size_small", default=u'Small')),
            ('medium', _(u"label_size_medium", default=u'Medium')),
            ('large', _(u"label_size_large", default=u'Large'))
        ),
        default="medium",
        enforceVocabulary = True
    ),
    BooleanField(
        name="showCarousel",
        widget=BooleanField._properties['widget'](
            label=_(u"label_show_carousel", default=u"Show Carousel?"),
        ),
        default=True
    ),
    BooleanField(
        name="showInfopane",
        widget=BooleanField._properties['widget'](
            label=_(u"label_show_info_pane", default=u"Show Info pane?"),
        ),
        default=True
    ),
    BooleanField(
        name="isTimed",
        widget=BooleanField._properties['widget'](
            label=_(u"label_timed", default=u"Timed?"),
            description=_(u"description_timed", 
                default=u"Should this gallery automatically change images for the user?"),
        ),
        default=False
    ),
    IntegerField(
        name='delay',
        widget=IntegerField._properties['widget'](
            label=_(u"label_delay", default=u"Delay"),
            description=_(u"description_delay", 
                default=u"If slide show is timed, the delay sets how long before the next image is shown in miliseconds.")
        ),
        required=1,
        default=5000
    ),
    IntegerField(
        name='fadeInDuration',
        widget=IntegerField._properties['widget'](
            label=_(u"label_fade_in_duration", default=u"Fade In Duration"),
            description=_(u"description_fade_in_duration", 
                default=u"The amount of time the fading effect should take in miliseconds.")
        ),
        required=1,
        default=500
    ),
    StringField(
        name="inTransition",
        widget=SelectionWidget(
            label=_(u"label_in_transition", default=u"Fade In Transition"),
            description=_(u"description_in_transition", 
                default="Select the transition you want to use when an image is being added."),
        ),
        vocabulary=TRANSITIONS,
        default="fade",
        enforceVocabulary = True
    ),
    IntegerField(
        name='fadeOutDuration',
        widget=IntegerField._properties['widget'](
            label=_(u"label_fade_out_duration", default="Fade Out Duration"),
            description=_(u"description_fade_out_duration",
                default=u"The amount of time the fading effect should take in miliseconds.")
        ),
        required=1,
        default=500
    ),
    StringField(
        name="outTransition",
        widget=SelectionWidget(
            label=_(u"label_out_transition", default="Fade Out Transition"),
            description=_(u"description_out_transition",
                default=u"Select the transition you want to use when an image is being removed.")
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