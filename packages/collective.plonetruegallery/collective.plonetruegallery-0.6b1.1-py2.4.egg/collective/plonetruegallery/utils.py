
class ginfo(object):
    name = None
    description = None
    t = None
    schema = None
    
    def __init__(self, name, desc, t, schema):
        self.name = name
        self.description = desc
        self.t = t
        self.schema = schema

GalleryTypes = []

def RegisterGalleryType(name, desc, t, schema):
    GalleryTypes.append(ginfo(name, desc, t, schema))

def getGalleryAdapter(gallery):
    for ginfo in GalleryTypes:
        if ginfo.name == gallery.getType():
            return ginfo.t(gallery)