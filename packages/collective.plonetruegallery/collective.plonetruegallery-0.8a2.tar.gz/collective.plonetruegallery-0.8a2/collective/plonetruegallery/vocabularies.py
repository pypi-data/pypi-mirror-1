from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from interfaces import IGallerySettings

class PTGVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value...
    This prevents any issues if a gallery or display
    type is removed and the user had it selected.
    """
    
    def __init__(self, terms, *interfaces, **config):
        super(PTGVocabulary, self).__init__(terms, *interfaces)
        
        if config.has_key('default'):
            self.default = config['default']
        else:
            self.default = None
        
    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.default]
        except:
            raise LookupError(value)

def DisplayTypeVocabulary(context):
    from collective.plonetruegallery.meta.zcml import DisplayTypes
    items = []
    for t in DisplayTypes:
        items.append(SimpleTerm(t.name, t.name, t.description))

    return PTGVocabulary(items, default=IGallerySettings['display_type'].default)
    
def GalleryTypeVocabulary(context):
    from collective.plonetruegallery.meta.zcml import GalleryTypes
    items = []
    for t in GalleryTypes:
        items.append(SimpleTerm(t.name, t.name, t.description))

    return PTGVocabulary(items, default=IGallerySettings['gallery_type'].default)
    
    