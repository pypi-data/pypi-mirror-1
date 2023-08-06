from zope.i18nmessageid import MessageFactory
PTGMessageFactory = MessageFactory("collective.plonetruegallery")

from meta.zcml import GalleryTypes, DisplayTypes
    
def getGalleryAdapter(gallery):
    for t in GalleryTypes:
        if t.name == gallery.getType():
            return t(gallery)
            
def getDisplayAdapter(gallery, request):
    for t in DisplayTypes:
        if t.name == gallery.getDisplayType():
            return t(gallery, request)