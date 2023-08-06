from interfaces import IGalleryType

GALLERY_TYPES = []

def AddGalleryType(klass):
    GALLERY_TYPES.append(klass)
        
def GalleryTypesVocabulary():
    vocab = []
    index = 0
    for gallery_type in GALLERY_TYPES:
        vocab.append([str(index), gallery_type().name() + ": " + gallery_type().description()])
        index = index + 1
        
    return vocab