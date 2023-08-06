DEFAULT_GALLERY_TYPE = "default"
PAGE_SIZE = 10
from collective.plonetruegallery.utils import PTGMessageFactory as _

TRANSITIONS = (
    ('fade', _(u"label_fade", default=u'Fade')),
#    ('slide', 'Slide'), #can't really get it to work well across the board...  remove for now...
    ('show', _(u"label_show", default=u'Show'))
)
        
def GalleryTypesVocabulary(GalleryTypes):
    vocab = []
    for ginfo in GalleryTypes:
        vocab.append([
            ginfo.name, 
            _(u"label_%s_gallery_type" % ginfo.name, 
                default=u"%s: %s" % (
                    ginfo.name,
                    ginfo.description
                )
            )
        ])
        
    return vocab