from zope.interface import implements
from interfaces import IBaseGallery

class BaseGallery:
    implements(IBaseGallery)
    
    def getImageUrl(self, image, subGallery=None):
        if subGallery:
            return "%s/%s/%s/image_%s" % (self.absolute_url(), subGallery.id, image.id, self.image_size)
        else:
            return "%s/%s/image_%s" % (self.absolute_url(), image.id, self.image_size)
        
    def getThumbUrl(self, image, subGallery=None):
        if subGallery:
            return "%s/%s/%s/image_thumb" % (self.absolute_url(), subGallery.id, image.id)
        else:
            return "%s/%s/image_thumb" % (self.absolute_url(), image.id)
    
    def getImageInfoDict(self, image):
        return {
            'image_url': self.getImageUrl(image), 
            'thumb_url': self.getThumbUrl(image),
            'link': self.absolute_url() + "/" + image.id,
            'title': image.Title,
            'description': image.Description 
        }