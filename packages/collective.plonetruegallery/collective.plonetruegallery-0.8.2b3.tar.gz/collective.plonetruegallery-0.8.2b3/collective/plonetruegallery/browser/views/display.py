from collective.plonetruegallery.interfaces import ISlideshowDisplayType, \
    IDisplayType, ISlideShowDisplaySettings, IBaseSettings, \
    IFancyBoxDisplaySettings, IHighSlideDisplaySettings, IGallery
from plone.memoize.view import memoize
from zope.interface import implements
from collective.plonetruegallery import PTGMessageFactory as _
from collective.plonetruegallery.settings import GallerySettings
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from os.path import basename
import AccessControl

# Check for Plone 4
try:
    from Products.CMFPlone.factory import _IMREALLYPLONE4
except ImportError:
    class PloneTrueGalleryPageTemplate(ViewPageTemplateFile):
        """
        Plone 3 compatible page template file.
        Make the pt_render call signature the same as the 
        zope.pagetemplate.pagetemplatefile.PageTemplateFile.pt_render method
        
        Also override pt_getContext since we've already done that for it.
        """
        
        def pt_getContext(self):
            return {}

        def pt_render(self, namespace):
            return super(PloneTrueGalleryPageTemplate, self).pt_render(extra_context=namespace)
        
else:
    class PloneTrueGalleryPageTemplate(PageTemplateFile):
        """
        Plone 4 compatible page template file. All it needs is the getId method...
        """

        def getId(self):
            return basename(self.filename)
        

class BaseDisplayType(object):
    implements(IDisplayType)
    
    name = None
    description = None
    schema = None
    template = None
    user_warning = None
    
    def __init__(self, galleryadapter):
        self.adapter = galleryadapter
        self.gallery = self.adapter.gallery
        self.request = self.adapter.request
        self.settings = GallerySettings(
            self.gallery, 
            interfaces=[self.adapter.schema, self.schema]
        )
        
    @property
    def height(self):
        return self.adapter.sizes[self.settings.size]['height']
    
    @property
    def width(self):
        return self.adapter.sizes[self.settings.size]['width']

    @memoize
    def get_start_image_index(self):
        if self.request.has_key('start_image'):
            si = self.request.get('start_image', '')
            images = self.adapter.cooked_images
            for index in range(0, len(images)):
                if si == images[index]['title']:
                    return index
        return 0

    start_image_index = property(get_start_image_index)


class BatchingDisplayType(BaseDisplayType):
    implements(IDisplayType)
    
    @memoize
    def uses_start_image(self):
        """
        disable start image if a batch start is specified.
        """
        return bool(self.request.has_key('start_image')) and \
            not bool(self.request.has_key('b_start'))
    
    @memoize
    def get_b_start(self):
        if self.uses_start_image():
            page = self.get_page()
            return page * self.settings.batch_size
        else:
            return int(self.request.get('b_start', 0))
    
    b_start = property(get_b_start)
    
    @memoize
    def get_start_image_index(self):
        if self.uses_start_image():
            index = super(BatchingDisplayType, self).get_start_image_index()
            return index - (self.get_page() * self.settings.batch_size)
        else:
            return 0
    
    start_image_index = property(get_start_image_index)    
    
    @memoize
    def get_page(self):
        index = super(BatchingDisplayType, self).get_start_image_index()
        return index / self.settings.batch_size
        
    @property
    @memoize
    def start_automatically(self):
        return self.uses_start_image() or \
            self.adapter.number_of_images < self.settings.batch_size


class SlideshowDisplayType(BaseDisplayType):
    implements(ISlideshowDisplayType)
    
    name = u"slideshow"
    template = PloneTrueGalleryPageTemplate('slideshow.pt')
    schema = ISlideShowDisplaySettings
    description = _(u"label_slideshow_display_type",
        default=u"Slideshow 2")
    
    offset = 10
    burns_zoom = 30
    
    # scaling can with an aspect ratio can make the images look ugly...
    # so we calculate the best possible size to ensure no distortion
    # this causes galleries to be a little smaller than what people
    # may expect, but we sacrifice this for better image quality
    image_buffer_ratio = 0.75 
    
    def get_width_and_height(self):
        width = self.width - (self.width - int((self.image_buffer_ratio * self.width)))
        height = self.height - (self.height - int((self.image_buffer_ratio * self.height)))
        if 'kenburns' in self.settings.slideshow_effect:
            width = width - self.burns_zoom
            height = height - self.burns_zoom
            
        return (width, height)
    
    def css(self):
        width, height = self.get_width_and_height()
        return """
        #plonetruegallery-container{
    	    width: %(width)ipx;
        }
        .plonetruegallery {
        	height: %(height)ipx;
        	width: %(width)ipx;
        }
        .plonetruegallery-images {
        	height: %(height)ipx;
        	width: %(width)ipx;
        }
        .plonetruegallery-thumbnails{
            bottom: -%(bottom)ipx;
            height: %(thumbnail_height)ipx;
        }
        
        .plonetruegallery-thumbnails ul{
            height: %(thumbnail_height)ipx;
        }
        #plonetruegallery-dropshadow{
            width: %(shadow_width)ipx;
        }
        #plonetruegallery-dropshadow tbody tr td.centermiddle {
            width: %(shadow_width)ipx;
            height: %(height)ipx;
        }
        """ % {
            'height' : height,
            'width' : width,
            'shadow_width' : width + 40,
            'thumbnail_height' : self.adapter.sizes['thumb']['height'],
            'bottom' : self.adapter.sizes['thumb']['height'] + (2*self.offset)
        }
    
    def assemble_image(self, image):
        if len(image['description']) == 0:
            image['description'] = image['title']

        image['description'] = image['description'].replace('"', "'")\
                                                   .replace("\n", " ")
        
        return """
            '%(image_url)s' : {href : "%(link)s", caption : "%(description)s", thumbnail : "%(thumb_url)s" }
        """ % image
            
    def image_data(self):
        return "{%s}" % (
            ','.join([self.assemble_image(image) for image in self.adapter.cooked_images])
        )
    
    def javascript(self):
        width, height = self.get_width_and_height()
        
        return """
	//<![CDATA[
window.addEvent('domready', function(){
var data = %(data)s;
var myShow = new %(class)s('show', data, {
    controller: true, 
    classes: ['plonetruegallery'],
    loader: {'animate': ['++resource++plonetruegallery.resources/slideshow/css/loader-#.png', 12]},
    thumbnails: %(show_carousel)s, 
    captions: %(show_infopane)s,
    width: %(width)i,
    height: %(height)i,
    paused: %(paused)s,
    delay: %(delay)i,
    duration: %(duration)s,
    slide: %(slide)i,
	zoom: [%(zoom)i, %(zoom)i]
});
if (myShow.options.thumbnails){
  ['a', 'b'].each(function(p){ 
	new Element('div', { 'class': 'overlay ' + p }).inject(myShow.slideshow.retrieve('thumbnails'));
  });
}

});
    	  	//]]>
        """ % {
            'data' : self.image_data(),
            'class' : self.settings.slideshow_effect.split(':')[1],
            'show_carousel' : str(self.settings.show_slideshow_carousel).lower(),
            'show_infopane' : str(self.settings.show_slideshow_infopane).lower(),
            'width' : width,
            'height' : height,
            'paused' : str( (not self.settings.timed) ).lower(),
            'delay' : self.settings.delay,
            'duration' : self.settings.duration,
            'slide' : self.start_image_index,
            'zoom' : self.burns_zoom
        }


class FancyBoxDisplayType(BatchingDisplayType):
    implements(IDisplayType)

    name = u"fancybox"
    template = PloneTrueGalleryPageTemplate('fancybox.pt')
    schema = IFancyBoxDisplaySettings
    description = _(u"label_fancybox_display_type",
        default=u"Fancy Box")
        
    def javascript(self):
        return """
var auto_start = %(start_automatically)s;
var start_image_index = %(start_index_index)i;
        """ % {
            'start_automatically' : str(self.start_automatically).lower(),
            'start_index_index' : self.start_image_index
        }
        

class HighSlideDisplayType(BatchingDisplayType):
    implements(IDisplayType)
    
    name = u"highslide"
    template = PloneTrueGalleryPageTemplate('highslide.pt')
    schema = IHighSlideDisplaySettings
    description = _(u"label_highslide_display_type",
        default=u"Highslide - verify terms of use")
    user_warning = _(u"label_highslide_user_warning",
        default=u"You can only use the Highslide gallery for non-commercial "
                u"use unless you purchase a commercial license. "
                u"Please visit http://highslide.com/ for details."
    )
        
    def javascript(self):
        outlineType = "hs.outlineType = '%s';" % self.settings.highslide_outlineType
        wrapperClassName = ''

        if 'drop-shadow' in outlineType:
            wrapperClassName = 'dark borderless floating-caption'
            outlineType = ''
        elif 'glossy-dark' in outlineType:
            wrapperClassName = 'dark'
            
        return """
hs.graphicsDir = '++resource++plonetruegallery.resources/highslide/graphics/';
hs.align = 'center';
hs.transitions = ['expand', 'crossfade'];
hs.fadeInOut = true;
hs.dimmingOpacity = 0.8;
%(outlineType)s
hs.wrapperClassName = %(wrapperClassName)s;
hs.captionEval = 'this.thumb.alt';
hs.marginBottom = 105; // make room for the thumbstrip and the controls
hs.numberPosition = 'caption';
hs.autoplay = %(timed)s;
hs.transitionDuration = %(duration)i;
hs.addSlideshow({
	interval: %(delay)i,
	repeat: true,
	useControls: true,
    fixedControls: 'fit',
	overlayOptions: {
		position: 'middle center',
		opacity: .7,
		hideOnMouseOut: true
	},
	thumbstrip: {
		position: 'bottom center',
		mode: 'horizontal',
		relativeTo: 'viewport'
	}
});

var auto_start = %(start_automatically)s;
var start_image_index = %(start_index_index)i;
        """ % {
            'outlineType' : outlineType,
            'wrapperClassName' : len(wrapperClassName) == 0 and 'null' or "'%s'" % wrapperClassName,
            'delay' : self.settings.delay,
            'timed' : str(self.settings.timed).lower(),
            'duration' : self.settings.duration,
            'start_automatically' : str(self.start_automatically).lower(),
            'start_index_index' : self.start_image_index
        }
