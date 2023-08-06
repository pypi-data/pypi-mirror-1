from collective.plonetruegallery.schemas.basic import BasicSchema
from collective.plonetruegallery.content.galleryimageinfo import GalleryImageInfo
from collective.plonetruegallery.interfaces import IBasicAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from Products.ATContentTypes.content.image import ATImageSchema
from zope.interface import implements
from zope.component import adapts
from collective.plonetruegallery.content.config import PAGE_SIZE
from collective.plonetruegallery.utils import RegisterGalleryType

NAME = u"default"
DESCRIPTION = u"Just Use Plone To Manage Images"

class BasicAdapter(object):
    implements(IBasicAdapter)
    adapts(IGallery)
    
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
        }
    }
    
    name = NAME
    description = DESCRIPTION
    
    def __init__(self, gallery):
        self.gallery = gallery
        
    def setup(self):
        pass
        
    def info(self):
        return {
            'count': len(self.gallery.objectIds()),
            'contents_url': self.gallery.absolute_url() + '/contents'
        }

    def getWidth(self):
        return self.sizes[self.gallery.getSize()]['width']

    def getHeight(self):
        return self.sizes[self.gallery.getSize()]['height']
        
    def getThumbnailWidth(self):
        return self.image_sizes['tile'][0]
        
    def getThumbnailHeight(self):
        return self.image_sizes['tile'][1]
        
    def getImageUrl(self, image):
		return "%s/%s/image_%s" % (self.gallery.absolute_url(), image.id, self.size_map[self.gallery.getSize()])

    def getThumbUrl(self, image):
		return "%s/%s/image_tile" % (self.gallery.absolute_url(), image.id)

    def assembleImageInfo(self, image):
        return GalleryImageInfo(
            image_url = self.getImageUrl(image), 
            thumb_url = self.getThumbUrl(image),
            link = self.gallery.absolute_url() + "/" + image.id,
            title = image.Title(),
            description = image.Description()
        )
            
    def numberOfImages(self):
        images = [i for i in self.gallery.objectIds() if self.gallery[i].meta_type == "ATImage"]
        return len(images)
        
    def getFirstImage(self):
        ids = self.gallery.objectIds()
        
        if len(ids) > 0:
            return self.assembleImageInfo(self.gallery[ids[0]])
        else:
            return None
        
    def images(self):
        images = [self.gallery[id] for id in self.gallery.objectIds()]
        return [self.assembleImageInfo(i) for i in images if i.meta_type == "ATImage"]

    def getPage(self, page):
        start = PAGE_SIZE*page
        end = (PAGE_SIZE*page) + PAGE_SIZE
        
        images = [self.gallery[id] for id in self.gallery.objectIds()[start:end]]
        return [self.assembleImageInfo(i) for i in images if i.meta_type == "ATImage"]
        
        
RegisterGalleryType(NAME, DESCRIPTION, IBasicAdapter, BasicSchema)