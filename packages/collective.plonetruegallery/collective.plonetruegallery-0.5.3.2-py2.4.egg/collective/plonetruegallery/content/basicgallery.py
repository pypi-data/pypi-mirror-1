from Products.ATContentTypes.content.image import ATImageSchema
from Products.Archetypes.atapi import Schema
from zope.interface import implements
from interfaces import IGalleryType, IBasicGalleryTypeValidator
from galleryimageinfo import GalleryImageInfo
from config import AddGalleryType, PAGE_SIZE
from Products.validation.interfaces.IValidator import IValidator
from validators import BaseGalleryTypeValidator

GALLERY_TYPE = "default"
BasicSchema = Schema()

class BasicGallery:
    """A folder which can contain other items."""

    implements(IGalleryType)

    _image_sizes  = ATImageSchema['image'].sizes
    _schema         =  BasicSchema
    
    sizes = {
        'small': {
            'width': _image_sizes['mini'][0],
            'height':_image_sizes['mini'][1]
        },
        'medium':{
            'width': _image_sizes['preview'][0],
            'height': _image_sizes['preview'][1],
        },
        'large':{
            'width': _image_sizes['large'][0],
            'height': _image_sizes['large'][1],
        }
    }
    
    def __init__(self, gallery=None):
        self._gallery = gallery
    
    def name(self):
        return GALLERY_TYPE
        
    def description(self):
        return "Just Use Plone To Manage Images"
    
    def getSchema(self):
        return self._schema.copy()
        
    def info(self):
        return {
            'count': len(self._gallery.objectIds()),
            'contents_url': self._gallery.absolute_url() + '/contents'
        }

    def getThumbnailWidth(self):
        return self._image_sizes['tile'][0]
        
    def getThumbnailHeight(self):
        return self._image_sizes['tile'][1]
        
    def getImageUrl(self, image, subGallery=None):
        if subGallery:
            return "%s/%s/%s/image_%s" % (self._gallery.absolute_url(), subGallery.id, image.id, self._gallery.image_size)
        else:
            return "%s/%s/image_%s" % (self._gallery.absolute_url(), image.id, self._gallery.image_size)

    def getThumbUrl(self, image, subGallery=None):
        if subGallery:
            return "%s/%s/%s/image_tile" % (self._gallery.absolute_url(), subGallery.id, image.id)
        else:
            return "%s/%s/image_tile" % (self._gallery.absolute_url(), image.id)

    def assembleImageInfo(self, image):
        return GalleryImageInfo(
            image_url = self.getImageUrl(image), 
            thumb_url = self.getThumbUrl(image),
            link = self._gallery.absolute_url() + "/" + image.id,
            title = image.Title(),
            description = image.Description()
        )
        
    def check_size(self):
        self._gallery.image_size = "mini"
        for size in self._image_sizes:
            if self._image_sizes[size][0] <= self._gallery.getWidth() or self._image_sizes[size][0] <= self._gallery.getHeight():
                if self._image_sizes[size][0] > self._image_sizes[self._gallery.image_size][0]:
                    self._gallery.image_size = size
            
    def numberOfImages(self):
        images = [i for i in self._gallery.objectIds() if self._gallery[i].meta_type == "ATImage"]
        return len(images)
        
    def getFirstImage(self):
        ids = self._gallery.objectIds()
        
        if len(ids) > 0:
            return self.assembleImageInfo(self._gallery[ids[0]])
        else:
            return None
        
    def images(self):
        images = [self._gallery[id] for id in self._gallery.objectIds()]
        return [self.assembleImageInfo(i) for i in images if i.meta_type == "ATImage"]

    def getPage(self, page):
        start = PAGE_SIZE*page
        end = (PAGE_SIZE*page) + PAGE_SIZE
        
        images = [self._gallery[id] for id in self._gallery.objectIds()[start:end]]
        return [self.assembleImageInfo(i) for i in images if i.meta_type == "ATImage"]

AddGalleryType(BasicGallery)