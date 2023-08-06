from zope.i18nmessageid import MessageFactory
PTGMessageFactory = MessageFactory("collective.plonetruegallery")

GalleryTypes = []
DisplayTypes = []

def RegisterGalleryType(t):
    GalleryTypes.append(t)

def RegisterDisplayType(t):
    DisplayTypes.append(t)
    
def getGalleryAdapter(gallery):
    for t in GalleryTypes:
        if t.name == gallery.getType():
            return t(gallery)
            
def getDisplayAdapter(gallery):
    for t in DisplayTypes:
        if t.name == gallery.getDisplayType():
            return t(gallery)