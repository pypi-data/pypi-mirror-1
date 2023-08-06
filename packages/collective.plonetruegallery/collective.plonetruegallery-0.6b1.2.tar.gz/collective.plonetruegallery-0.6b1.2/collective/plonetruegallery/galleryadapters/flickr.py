from collective.plonetruegallery.interfaces import IFlickrAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from collective.plonetruegallery.content.galleryimageinfo import GalleryImageInfo
from collective.plonetruegallery.schemas.flickr import FlickrSchema
from zope.interface import implements
from zope.component import adapts
from collective.plonetruegallery.galleryadapters.basic import BasicAdapter
from collective.plonetruegallery.content.config import PAGE_SIZE
from collective.plonetruegallery.utils import RegisterGalleryType

HAS_FLICKR_API_INSTALLED = True
API_KEY = "9b354d88fb47b772fee4f27ab15d6854"

try:
    import flickrapi
except:
    HAS_FLICKR_API_INSTALLED = False

NAME = "flickr"
DESCRIPTION = "A Gallery That Uses Flickr Set For Images"

class FlickrAdapter(object):
    implements(IFlickrAdapter)
    adapts(IGallery)
    
    schema =  FlickrSchema
    name = NAME
    description = DESCRIPTION
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
        'flickr':{
            'small': '_m',
            'medium': '',
            'large': '_b'
        }
    }
    
    def __init__(self, gallery=None):
        self.gallery = gallery

    def assembleImageInfo(self, image):
        return GalleryImageInfo(
            image_url = self.getLargePhotoURL(image), 
            thumb_url = self.getMiniPhotoURL(image),
            link = self.getPhotoLink(image),
            title = image['title'],
            description = ""
        )
        
    def getWidth(self):
        return self.sizes[self.gallery.getSize()]['width']

    def getHeight(self):
        return self.sizes[self.gallery.getSize()]['height']
        
    def getThumbnailWidth(self):
        return 75

    def getThumbnailHeight(self):
        return 75
        
    def check_size(self):
        pass
         
    def info(self):
        return {
            'count': self.getCount(),
            'contents_url': self.getSetUrl(),
            'slideshow_url': self.getSlideshowUrl()
        }
        
    def getSetUrl(self):
        return "http://www.flickr.com/photos/%s/sets/%s/" % (
            self.gallery.flickr_userid, 
            self.gallery.flickr_photosetid
        )
        
    def getSlideshowUrl(self):
        return "http://www.flickr.com/photos/%s/sets/%s/show/" % (
            self.gallery.flickr_userid, 
            self.gallery.flickr_photosetid
        )
        
    def getFlickrUserid(self, username):
        flickr = flickrapi.FlickrAPI(API_KEY)
        
        id = None
        try:
            id = flickr.people_findByUsername(username=username).user[0]['nsid']
        except:
            try:
                id = flickr.people_getInfo(user_id=username).person[0]['nsid']
            except:
                pass
        
        return id
        
    def getCount(self):
        flickr = flickrapi.FlickrAPI(API_KEY)
        info = flickr.photosets_getInfo(user_id=self.gallery.flickr_userid, photoset_id=self.gallery.flickr_photosetid)
        
        return info.photoset[0]['photos']
        
    def getFlickrPhotosetId(self, theset, userid=None):
        if userid is None:
            userid = self.gallery.flickr_userid
        
        flickr = flickrapi.FlickrAPI(API_KEY)
        sets = flickr.photosets_getList(user_id=userid)
        
        for photoset in sets.photosets[0].photoset:
            if photoset.title[0].text == theset or photoset['id'] == theset:
                return photoset['id']
                
        return None

    def getMiniPhotoURL(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (
            photo['farm'], 
            photo['server'], 
            photo['id'], 
            photo['secret'], 
        )
        
    def getPhotoLink(self, photo):
        return "http://www.flickr.com/photos/%s/%s/sizes/o/" % (
            self.gallery.flickr_userid,
            photo['id']
        )
        
    def getLargePhotoURL(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s%s.jpg" % (
            photo['farm'], 
            photo['server'], 
            photo['id'],
            photo['secret'],
            self.sizes['flickr'][self.gallery.getSize()]
        )
        
    def flickr(self):
        return  flickrapi.FlickrAPI(API_KEY)
        
    def numberOfImages(self):
        try:
            flickr = self.flickr()
            return flickr.photosets_getInfo(photoset_id=self.gallery.flickr_photosetid).photoset[0]['photos']
        except:
            return 0
        
    def getFirstImage(self):
        try:
            flickr = flickrapi.FlickrAPI(API_KEY)
            photos = flickr.photosets_getPhotos(
                user_id=self.gallery.flickr_userid, 
                photoset_id=self.gallery.flickr_photosetid,
                per_page=1,
                page=1
            )
            
            return self.assembleImageInfo(photos.photoset[0].photo[0])
        except:
            return None
    
    def getPage(self, page):
        try:
            flickr = flickrapi.FlickrAPI(API_KEY)
            photos = flickr.photosets_getPhotos(
                user_id=self.gallery.flickr_userid, 
                photoset_id=self.gallery.flickr_photosetid,
                per_page=PAGE_SIZE,
                page=(int(page)+1)
            )
            
            return [self.assembleImageInfo(image) for image in photos.photoset[0].photo]
        except:
            return []
    
    def images(self):
        try:
            flickr = flickrapi.FlickrAPI(API_KEY)
            photos = flickr.photosets_getPhotos(
                user_id=self.gallery.flickr_userid, 
                photoset_id=self.gallery.flickr_photosetid,
            )
        
            return [self.assembleImageInfo(image) for image in photos.photoset[0].photo] 
        except:
            return []
            
if HAS_FLICKR_API_INSTALLED:
    RegisterGalleryType(NAME, DESCRIPTION, IFlickrAdapter, FlickrSchema)