from collective.plonetruegallery.interfaces import IGenerator
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.content.gallery import Gallery
from zope.interface import implements
from zope.component import adapts

class Generator(object):
    implements(IGenerator)
    adapts(Gallery)
    
    def __init__(self, gallery):
        self.gallery = gallery
        self.adapter = getGalleryAdapter(self.gallery)
    
    def css(self):
        return """
    	.jcarousel-skin-truegallery .jcarousel-clip-horizontal {
            height: %spx;
        }
        .jcarousel-skin-truegallery .jcarousel-item {
            width: %spx;
            height: %spx;
        }
        """ % (
            self.adapter.getThumbnailHeight() + 10,
            self.adapter.getThumbnailWidth(),
            self.adapter.getThumbnailHeight()
        )
    
    def javascript(self):
        return """
        jq(document).ready(function(){
            document.trueGallery = new TrueGallery(jq('div#plone-true-gallery'), {
                image_width: %i,
                image_height: %i,
                thumbnail_width: %i,
                thumbnail_height: %i,
                timed: %s,
                delay: %i,
                hideSpeed: %i,
                hideType: '%s',
                showSpeed: %i,
                showType: '%s',
                showInfo: %s,
                showCarousel: %s
            });
        });
        """ % (
            self.adapter.getWidth(),
            self.adapter.getHeight(),
            self.adapter.getThumbnailWidth(),
            self.adapter.getThumbnailHeight(),
            str(self.gallery.getIsTimed()).lower(),
            self.gallery.getDelay(),
            self.gallery.getFadeOutDuration(),
            self.gallery.getOutTransition(),
            self.gallery.getFadeInDuration(),
            self.gallery.getInTransition(),
            str(self.gallery.getShowInfopane()).lower(),
            str(self.gallery.getShowCarousel()).lower()
        )