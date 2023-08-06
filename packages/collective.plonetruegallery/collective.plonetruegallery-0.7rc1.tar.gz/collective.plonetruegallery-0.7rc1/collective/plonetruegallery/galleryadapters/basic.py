from collective.plonetruegallery.schemas.basic import BasicSchema
from collective.plonetruegallery.interfaces import IBasicAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from Products.ATContentTypes.content.image import ATImageSchema
from zope.interface import implements
from zope.component import adapts
from base import BaseAdapter
from collective.plonetruegallery.utils import PTGMessageFactory as _

class BasicAdapter(BaseAdapter):
    implements(IBasicAdapter)
    
    name = u"default"
    description = _(u"label_default_gallery_type", 
        default=u"default: Just Use Plone To Manage Images")
    
    image_sizes = ATImageSchema['image'].sizes
    schema =  BasicSchema.copy()

    size_map = {
		'small' : 'mini',
		'medium' : 'preview',
		'large' : 'large'
	}

    sizes = {
        'small': {
            'width': image_sizes['mini'][0],
            'height':image_sizes['mini'][1]
        },
        'medium':{
            'width': image_sizes['preview'][0],
            'height': image_sizes['preview'][1]
        },
        'large':{
            'width': image_sizes['large'][0],
            'height': image_sizes['large'][1]
        },
        'thumbnail': {
            'width' : image_sizes['tile'][0],
            'height' : image_sizes['tile'][0]
        }
    }
        
    def get_image_url(self, image):
		return "%s/%s/image_%s" % (self.gallery.absolute_url(), image.id, self.size_map[self.gallery.getSize()])

    def get_thumb_url(self, image):
		return "%s/%s/image_tile" % (self.gallery.absolute_url(), image.id)

    def assemble_image_information(self, image):
        return {
            'image_url' : self.get_image_url(image), 
            'thumb_url' : self.get_thumb_url(image),
            'link' : self.gallery.absolute_url() + "/" + image.id,
            'title' : image.Title(),
            'description' : image.Description()
        }
        
    def retrieve_images(self):
        images = [self.gallery[id] for id in self.gallery.objectIds()]
        return [self.assemble_image_information(i) for i in images if i.meta_type == "ATImage"]
        
        