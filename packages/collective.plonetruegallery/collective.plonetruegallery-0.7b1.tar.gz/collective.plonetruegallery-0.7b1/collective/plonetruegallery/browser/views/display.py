from collective.plonetruegallery.interfaces import IClassicDisplayType, ISlideshowDisplayType, IDisplayType
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from zope.interface import implements
from zope.component import adapts
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

class BaseDisplayType(object):
    implements(IDisplayType)
    
    name = None
    description = None
    
    def __init__(self, gallery):
        
        self.gallery = gallery
        self.adapter = getGalleryAdapter(self.gallery)
        
        self.gallery_size = self.gallery.getSize()
        
        self.height = self.adapter.sizes[self.gallery_size]['height']
        self.width = self.adapter.sizes[self.gallery_size]['width']
        self.thumbnail_width = self.adapter.sizes['thumbnail']['width']
        self.thumbnail_height = self.adapter.sizes['thumbnail']['width']

    def css(self):
        raise Exception("Not implemented")
        
    def javascript(self):
        raise Exception("Not implemented")

class ClassicDisplayType(BaseDisplayType):
    implements(IClassicDisplayType)
    
    name = u"classic"
    description = u"The original slideshow for plonetruegallery"
    
    def css(self):
        return """
    	.jcarousel-skin-truegallery .jcarousel-clip-horizontal {
            height: %spx;
        }
        .jcarousel-skin-truegallery .jcarousel-item {
            width: %spx;
            height: %spx;
        }
        div#plone-true-gallery{
            width: %spx;
        }
        """ % (
            self.adapter.sizes['thumbnail']['height'] + 10,
            self.adapter.sizes['thumbnail']['width'],
            self.adapter.sizes['thumbnail']['height'],
            self.width + 100
        )
    
    def javascript(self):
        return """
        jQuery(document).ready(function(){
            document.trueGallery = new TrueGallery(jQuery('div#plone-true-gallery'), {
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
            str(self.gallery.getIsTimed()).lower(),
            self.gallery.getDelay(),
            self.gallery.getImageChangeDuration(),
            self.gallery.getClassicTransition(),
            self.gallery.getImageChangeDuration(),
            self.gallery.getClassicTransition(),
            str(self.gallery.getShowInfopane()).lower(),
            str(self.gallery.getShowCarousel()).lower()
        )

class SlideshowDisplayType(BaseDisplayType):
    implements(ISlideshowDisplayType)
    
    name = "slideshow"
    description = "Slideshow 2 javascript gallery"
    
    def css(self):
        
        return """
        .plonetruegallery {
        	height: %(height)ipx;
        	width: %(width)ipx;
        }
        .plonetruegallery-images {
        	height: %(height)ipx;
        	width: %(width)ipx;
        }
        .plonetruegallery-thumbnails{
            bottom: -%(thumbnail_height)ipx;
            height: %(thumbnail_height)ipx;
        }
        .plonetruegallery-thumbnails ul {
        	height: %(thumbnail_height)spx;
        """ % {
            'height' : self.height,
            'width' : self.width,
            'thumbnail_height' : self.thumbnail_height,
            'thumbnail_width' : self.thumbnail_width
        }
    
    def image_data(self):
        def assemble(image):
            return """
                '%(image_url)s' : {caption : "%(description)s", thumbnail : "%(thumb_url)s" }
            """ % image
            
        return "{%s}" % (
            ','.join([assemble(image) for image in self.adapter.get_all_cooked_images()])
        )
    
    def javascript(self):
        
        return """
	//<![CDATA[
    	  window.addEvent('domready', function(){
    	    var data = %s;
    	    var myShow = new %s('show', data, {
    	        controller: true, 
    	        classes: ['plonetruegallery'],
    	        loader: {'animate': ['++resource++plonetruegallery.resources/slideshow/css/loader-#.png', 12]},
    	        thumbnails: %s, 
    	        captions: %s,
    	        width: %i,
    	        height: %i,
    	        paused: %s,
    	        delay: %i,
    	        duration: %s
    	    });
    	  });
    	  	//]]>
        """ % (
            self.image_data(),
            self.gallery.getSlideshowEffect().split(':')[1],
            str(self.gallery.getShowCarousel()).lower(),
            str(self.gallery.getShowInfopane()).lower(),
            self.width,
            self.height,
            str( (not self.gallery.getIsTimed()) ).lower(),
            self.gallery.getDelay(),
            self.gallery.getImageChangeDuration()
        )