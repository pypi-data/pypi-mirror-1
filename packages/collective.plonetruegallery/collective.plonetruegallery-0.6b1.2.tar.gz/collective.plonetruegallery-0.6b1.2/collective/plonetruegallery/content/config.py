DEFAULT_GALLERY_TYPE = "default"
PAGE_SIZE = 10

TRANSITIONS = (
    ('fade', 'Fade'),
#    ('slide', 'Slide'), #can't really get it to work well across the board...  remove for now...
    ('show', 'Show')
)
        
def GalleryTypesVocabulary(GalleryTypes):
    vocab = []
    for ginfo in GalleryTypes:
        vocab.append([
            ginfo.name, 
            "%s: %s" % (
                ginfo.name,
                ginfo.description
            )
        ])
        
    return vocab