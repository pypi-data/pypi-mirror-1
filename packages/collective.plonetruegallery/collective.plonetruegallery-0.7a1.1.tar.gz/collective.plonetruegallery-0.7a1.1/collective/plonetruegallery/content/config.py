DEFAULT_GALLERY_TYPE = "default"
PAGE_SIZE = 15
from collective.plonetruegallery.utils import PTGMessageFactory as _

TRANSITIONS = (
    ('fade', _(u"label_fade", default=u'Fade')),
    ('show', _(u"label_show", default=u'Show'))
)
        
def GalleryTypesVocabulary(GalleryTypes):
    vocab = []
    for t in GalleryTypes:
        vocab.append([
            t.name, 
            _(u"label_%s_gallery_type" % t.name, 
                default=u"%s: %s" % (
                    t.name,
                    t.description
                )
            )
        ])
        
    return vocab