from collective.plonetruegallery.interfaces import IFlickrAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from collective.plonetruegallery.schemas.flickr import FlickrSchema
from zope.interface import implements
from zope.component import adapts
from collective.plonetruegallery.config import FLICKR_API_VERSION
from base import BaseAdapter

import time
from DateTime import DateTime

API_KEY = "9b354d88fb47b772fee4f27ab15d6854"

try:
    import flickrapi
except:
    pass

def add_condition():    
    try:
        import flickrapi
    
        if float(flickrapi.__version__) < FLICKR_API_VERSION:
            return False
    
    except:
        return False
        
    return True

class FlickrAdapter(BaseAdapter):
    implements(IFlickrAdapter)
    
    schema =  FlickrSchema
    name = u"flickr"
    description = u"A Gallery That Uses Flickr Set For Images"
    sizes = {
        'small': {
            'width': 240,
            'height': 180
        },
        'medium':{
            'width': 500,
            'height': 375
        },
        'large':{
            'width': 1024,
            'height': 768
        },
        'thumbnail' : {
            'width' : 72,
            'height' : 72
        },
        'flickr':{
            'small': '_m',
            'medium': '',
            'large': '_b'
        }
    }

    def assemble_image_information(self, image):
        return {
            'image_url' : self.get_large_photo_url(image), 
            'thumb_url' : self.get_mini_photo_url(image),
            'link' : self.get_photo_link(image),
            'title' : image.get('title'),
            'description' : ""
        }
        
    def get_flickr_user_id(self, username):
        flickr = flickrapi.FlickrAPI(API_KEY)
        
        id = None
        try:
            id = flickr.people_findByUsername(username=username).find('user').get('nsid')
        except:
            try:
                id = flickr.people_getInfo(user_id=username).find('person').get('nsid')
            except Exception, inst:
                self.log_error(Exception, inst, "Can't find filckr user id")
        
        return id
        
    def get_flickr_photoset_id(self, theset, userid=None):
        if userid is None:
            userid = self.gallery.flickr_userid
        
        flickr = flickrapi.FlickrAPI(API_KEY)
        sets = flickr.photosets_getList(user_id=userid)
        
        for photoset in sets.find('photosets').getchildren():
            if photoset.find('title').text == theset or photoset.get('id') == theset:
                return photoset.get('id')
                
        return None

    def get_mini_photo_url(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (
            photo.get('farm'), 
            photo.get('server'), 
            photo.get('id'), 
            photo.get('secret'), 
        )
        
    def get_photo_link(self, photo):
        return "http://www.flickr.com/photos/%s/%s/sizes/o/" % (
            self.gallery.flickr_userid,
            photo.get('id')
        )
        
    def get_large_photo_url(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s%s.jpg" % (
            photo.get('farm'), 
            photo.get('server'), 
            photo.get('id'),
            photo.get('secret'),
            self.sizes['flickr'][self.gallery.getSize()]
        )
        
    def flickr(self):
        return  flickrapi.FlickrAPI(API_KEY)
    
    def retrieve_images(self):
        try:
            flickr = flickrapi.FlickrAPI(API_KEY)
            photos = flickr.photosets_getPhotos(
                user_id=self.gallery.flickr_userid, 
                photoset_id=self.gallery.flickr_photosetid,
                media='photos'
            )
        
            return [self.assemble_image_information(image) for image in photos.find('photoset').getchildren()] 
        except Exception, inst:
            self.log_error(Exception, inst, "Error getting all images")
            return []