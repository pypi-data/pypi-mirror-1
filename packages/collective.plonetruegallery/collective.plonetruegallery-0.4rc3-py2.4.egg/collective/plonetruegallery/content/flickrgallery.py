from interfaces import IGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from interfaces import IGalleryType
from galleryimageinfo import GalleryImageInfo
from config import AddGalleryType
from Products.validation.interfaces.IValidator import IValidator

HAS_FLICKR_API_INSTALLED = True
API_KEY = "9b354d88fb47b772fee4f27ab15d6854"
GALLERY_TYPE = "flickr"

try:
    import flickrapi
except:
    HAS_FLICKR_API_INSTALLED = False


schema = Schema((
    StringField(
        name="flickrUsername",
        widget=StringField._properties['widget'](
            label="The username of your flickr account"
        ),
        schemata=GALLERY_TYPE
    ),
    StringField(
        name="flickrSet",
        widget=StringField._properties['widget'](
            label="Set",
            description="Name of your flickr set."
        ),
        schemata=GALLERY_TYPE
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
            description = "",
            width=self._gallery.getWidth()
        )
        
    def check_size(self):
        pass
         
    def getFlickrUserid(self, username):
        flickr = flickrapi.FlickrAPI(API_KEY)
        username = flickr.people_findByUsername(username=username)
        
        return username.user[0]['nsid']
        
    def getFlickrPhotosetId(self, theset):
        flickr = flickrapi.FlickrAPI(API_KEY)
        sets = flickr.photosets_getList(user_id=self._gallery.flickr_userid)
        
        for photoset in sets.photosets[0].photoset:
            if photoset.title[0].text == theset:
                return photoset['id']
                
        return None

    def getMiniPhotoURL(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % (
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
        return "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (
            photo['farm'], 
            photo['server'], 
            photo['id'],
            photo['secret']
        )
    
    def images(self):
        flickr = flickrapi.FlickrAPI(API_KEY)
        photos = flickr.photosets_getPhotos(
            user_id=self._gallery.flickr_userid, 
            photoset_id=self._gallery.flickr_photosetid, 
            extra='original_format,originalsecret'
        )
            
        return [self.assembleImageInfo(image) for image in photos.photoset[0].photo] 
        
    def validate(self, value, kwargs):
        gallery = kwargs['instance']
        req = kwargs['REQUEST']
        
        username = req.get('flickrUsername')
        photoset = req.get('flickrSet')
        
        try:
            gallery.flickr_userid = self.getFlickrUserid(username)
            gallery.flickr_photosetid = self.getFlickrPhotosetId(photoset)
            
            if gallery.flickr_userid is None or gallery.flickr_photosetid is None:
                return ("Flickr Error: Could not find flickr set for that user.  Please check flickr field values and make sure you have public access assigned for the set.")
            else:
                return True
        except:
            return ("Flickr Error: Could not find flickr set for that user.  Please check flickr field values and make sure you have public access assigned for the set.")
    
if HAS_FLICKR_API_INSTALLED:
    AddGalleryType(FlickrGallery)