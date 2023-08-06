from interfaces import IGalleryType

DEFAULT_GALLERY_TYPE = "default"
GALLERY_TYPES = {}
PAGE_SIZE = 15

def AddGalleryType(klass):
    if klass not in GALLERY_TYPES.values():
        GALLERY_TYPES[klass().name()] = klass
        
def GalleryTypesVocabulary():
    vocab = []
    for name, gallery_type in GALLERY_TYPES.items():
        vocab.append([
            name, 
            "%s: %s" % (
                name,
                gallery_type().description()
            )
        ])
        
    return vocab