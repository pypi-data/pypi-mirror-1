from Products.Archetypes.atapi import *
from zope.interface import implements
from interfaces import IGalleryType, IBasicGalleryTypeValidator
from galleryimageinfo import GalleryImageInfo
from config import AddGalleryType, PAGE_SIZE
from Products.validation.interfaces.IValidator import IValidator
from validators import BaseGalleryTypeValidator


HAS_FLICKR_API_INSTALLED = True
API_KEY = "9b354d88fb47b772fee4f27ab15d6854"
GALLERY_TYPE = "flickr"

try:
    import flickrapi
except:
    HAS_FLICKR_API_INSTALLED = False

class ValidateFlickrUsername(BaseGalleryTypeValidator):
    implements(IBasicGalleryTypeValidator)
        
    def canValidate(self, gallery_type):
        return gallery_type == GALLERY_TYPE
        
    def __call__(self, username, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        
        if self.canValidate(req.get('type')):
            try:
                gallery.flickr_userid = FlickrGallery().getFlickrUserid(username)
                if gallery.flickr_userid is None:
                    return ("Flickr Error: Could not validate flickr user.")
            except:
                return ("Flickr Error: Could not validate flickr user.")

        return True


class ValidateFlickrSet(BaseGalleryTypeValidator):
    implements(IBasicGalleryTypeValidator)

    def canValidate(self, gallery_type):
        return gallery_type == GALLERY_TYPE
    
    def __call__(self, photoset, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']

        if self.canValidate(req.get('type')):
            try:
                flickr_gallery_type = FlickrGallery()
                userid = flickr_gallery_type.getFlickrUserid(req.get('flickrUsername'))
                gallery.flickr_photosetid = flickr_gallery_type.getFlickrPhotosetId(photoset, userid)

                if gallery.flickr_photosetid is None:
                    return ("Flickr Error: Could not find flickr set.")
            except:
                return ("Flickr Error: Could not find flickr set.")

        return True
    

schema = Schema((
    StringField(
        name="flickrUsername",
        widget=StringField._properties['widget'](
            label="The username/id of your flickr account"
        ),
        schemata=GALLERY_TYPE,
        validators=(ValidateFlickrUsername(),)
    ),
    StringField(
        name="flickrSet",
        widget=StringField._properties['widget'](
            label="Set",
            description="Name/id of your flickr set."
        ),
        schemata=GALLERY_TYPE,
        validators=(ValidateFlickrSet(),)
    ),
),
)

FlickrGallerySchema = schema.copy()

class FlickrGallery:
    """A folder which can contain other items."""
    
    implements(IGalleryType)
    
    #hack for password field that loses password on validation...
    _schema         =  FlickrGallerySchema
    _flickr = None
    
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
        self._gallery = gallery
    
    def name(self):
        return GALLERY_TYPE
    
    def description(self):
        return "A Gallery That Uses Flickr Set For Images"
    
    def getSchema(self):
        return self._schema.copy()

    def assembleImageInfo(self, image):
        return GalleryImageInfo(
            image_url = self.getLargePhotoURL(image), 
            thumb_url = self.getMiniPhotoURL(image),
            link = self.getPhotoLink(image),
            title = image['title'],
            description = ""
        )
        
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
            self._gallery.flickr_userid, 
            self._gallery.flickr_photosetid
        )
        
    def getSlideshowUrl(self):
        return "http://www.flickr.com/photos/%s/sets/%s/show/" % (
            self._gallery.flickr_userid, 
            self._gallery.flickr_photosetid
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
        info = flickr.photosets_getInfo(user_id=self._gallery.flickr_userid, photoset_id=self._gallery.flickr_photosetid)
        
        return info.photoset[0]['photos']
        
    def getFlickrPhotosetId(self, theset, userid=None):
        
        if userid is None:
            userid = self._gallery.flickr_userid
        
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
            self._gallery.flickr_userid,
            photo['id']
        )
        
    def getLargePhotoURL(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s%s.jpg" % (
            photo['farm'], 
            photo['server'], 
            photo['id'],
            photo['secret'],
            self.sizes['flickr'][self._gallery.getSize()]
        )
    
    def getFirstImage(self):
        try:
            flickr = flickrapi.FlickrAPI(API_KEY)
            photos = flickr.photosets_getPhotos(
                user_id=self._gallery.flickr_userid, 
                photoset_id=self._gallery.flickr_photosetid,
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
                user_id=self._gallery.flickr_userid, 
                photoset_id=self._gallery.flickr_photosetid,
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
                user_id=self._gallery.flickr_userid, 
                photoset_id=self._gallery.flickr_photosetid,
            )
        
            return [self.assembleImageInfo(image) for image in photos.photoset[0].photo] 
        except:
            return []
        
if HAS_FLICKR_API_INSTALLED:
    AddGalleryType(FlickrGallery)