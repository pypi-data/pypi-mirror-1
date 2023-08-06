from Products.Archetypes.atapi import *
from zope.interface import implements
from interfaces import IGalleryType, IBasicGalleryTypeValidator
from galleryimageinfo import GalleryImageInfo
from config import AddGalleryType, PAGE_SIZE
from Products.validation.interfaces.IValidator import IValidator
from validators import BaseGalleryTypeValidator

HAS_GDATA_PACKAGE_INSTALLED = True
GALLERY_TYPE = "picasa"

try:
    import gdata.photos.service
    import gdata.media
    import gdata.geo
    from gdata.photos.service import GooglePhotosException
except:
    HAS_GDATA_PACKAGE_INSTALLED = False

class ValidatePicasaPassword(BaseGalleryTypeValidator):
    implements(IBasicGalleryTypeValidator)
        
    def canValidate(self, gallery_type):
        return gallery_type == GALLERY_TYPE
        
    def __call__(self, password, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        
        if self.canValidate(req.get('type')) and req.get('isPicasaPrivate'):
            try:
                gd_client = gdata.photos.service.PhotosService()
                gd_client.email = req.get('picasaUsername')
                #not working...
                gd_client.password = password
                gd_client.ProgrammaticLogin()
            except:
                return ("Picasa Error: Incorrect username or password.")

        return True
        
class ValidateIsPicasaPrivate(BaseGalleryTypeValidator):
    implements(IBasicGalleryTypeValidator)

    def canValidate(self, gallery_type):
        return gallery_type == GALLERY_TYPE

    def __call__(self, private, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']

        if self.canValidate(req.get('type')) and private:
            new_password = req.get('picasaPassword')
            
            if len(new_password) == 0 and len(gallery.getPicasaPassword()) == 0:
                return ("Picasa Error: You must enter a password if it is a private album.")

        return True
        
class ValidatePicasaAlbum(BaseGalleryTypeValidator):
    implements(IBasicGalleryTypeValidator)

    def canValidate(self, gallery_type):
        return gallery_type == GALLERY_TYPE

    def __call__(self, album, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']

        if self.canValidate(req.get('type')):
            try:
                gd_client = gdata.photos.service.PhotosService()
                gd_client.email = req.get('picasaUsername')
            
                if req.get('isPicasaPrivate'):
                    password = req.get('picasaPassword')
                    if len(password) == 0:
                        password = gallery.getPicasaPassword()
                    gd_client.password = password
                    gd_client.ProgrammaticLogin()
                
                feed = gd_client.GetUserFeed(user=req.get('picasaUsername'))
                for entry in feed.entry:
                    if entry.title.text == album or entry.name.text == album:
                        return True
            except:
                pass
    
            return ("Picasa Error: Could not find album.")

        return True
        
schema = Schema((
    StringField(
        name="picasaUsername",
        widget=StringField._properties['widget'](
            label="Email address of who this album belongs to"
        ),
        schemata=GALLERY_TYPE
    ),
    #can't figure out how to not make the user enter in their password on every edit
    #postback = True and populate = True doesn't work
    StringField(
        name="picasaPassword",
        widget=PasswordWidget(
            label="Password",
            description="Only required if your album is not public.  It is recommended to just make your album public.",
        ),
        schemata=GALLERY_TYPE,
        validators=(ValidatePicasaPassword(),)
    ),
    BooleanField(
        name="isPicasaPrivate",
        widget=BooleanField._properties['widget'](
            label="Is this a private album?",
            description="Password is required if it is."
        ),
        default=False,
        schemata=GALLERY_TYPE,
        validators=(ValidateIsPicasaPrivate(),)
    ),
    StringField(
        name="picasaAlbum",
        widget=StringField._properties['widget'](
            label="Album",
            description="Name of your picasa web album."
        ),
        schemata=GALLERY_TYPE,
        validators=(ValidatePicasaAlbum(),)
    ),
),
)

PicasaGallerySchema = schema.copy()

class PicasaGallery:
    """A folder which can contain other items."""
    
    implements(IGalleryType)
    
    #hack for password field that loses password on validation...
    _picasa_sizes = (200, 288, 320, 400, 512, 576, 640, 720, 800)
    _schema         =  PicasaGallerySchema
    
    _thumbnail_size = 72
    
    sizes = {
        'small': {
            'width': 200,
            'height': 200
        },
        'medium':{
            'width': 576,
            'height': 576
        },
        'large':{
            'width': 800,
            'height': 800
        }
    }
    
    def __init__(self, gallery=None):
        self._gallery = gallery
    
    def name(self):
        return GALLERY_TYPE

    def getThumbnailWidth(self):
        return self._thumbnail_size

    def getThumbnailHeight(self):
        return self._thumbnail_size

    def description(self):
        return "A Gallery That Uses a Picasa Web Album For its Images"
    
    def getSchema(self):
        return self._schema.copy()
        
    def info(self):
        feed = self.feed()
        return {
            'count': len(feed.entry),
            'contents_url': feed.GetHtmlLink().href
        }
        
    def authenticatePicasa(self, gd_client):
        gd_client.email = self._gallery.getPicasaUsername()
        gd_client.password = self._gallery.getPicasaPassword()
        gd_client.ProgrammaticLogin()

    def assembleImageInfo(self, image):
        return GalleryImageInfo(
            image_url = image.content.src, 
            thumb_url = image.media.thumbnail[0].url,
            link = image.content.src,
            title = image.title.text,
            description = image.summary.text 
        )
        
    def check_size(self):
        self._gallery.image_size = self._picasa_sizes[0]
        for size in self._picasa_sizes:
            if size <= self._gallery.getWidth() or size <= self._gallery.getHeight():
                if size > self._gallery.image_size:
                    self._gallery.image_size = size
        
    def feed(self):
        gd_client = gdata.photos.service.PhotosService()
        if self._gallery.getIsPicasaPrivate():
            self.authenticatePicasa(gd_client)

        try:
            return gd_client.GetFeed('/data/feed/api/user/%s/album/%s?kind=photo&imgmax=%su&thumbsize=%s' % (
                self._gallery.getPicasaUsername(), 
                self._gallery.getPicasaAlbum(), 
                self.sizes[self._gallery.getSize()]['width'],
                self._thumbnail_size)
            )
        except:
            #Do not show anything if connection failed
            return []
    

    def getFirstImage(self):
        try:
            picasaGallery = self.feed()
            return self.assembleImageInfo(picasaGallery.entry[0])
        except:
            return None

    def getPage(self, page):
        start = PAGE_SIZE*page
        end = (PAGE_SIZE*page) + PAGE_SIZE
        
        try:
            picasaGallery = self.feed()
            images = [self.assembleImageInfo(i) for i in picasaGallery.entry[start:end]]
            return images
        except:
            return []
    
    def images(self):
        picasaGallery = self.feed()
        images = [self.assembleImageInfo(i) for i in picasaGallery.entry]
        if images is None:
            self._gallery.error = True
            self._gallery.errorMsg = "Could not connect to album %s" % self._gallery.getPicasaAlbum()
            
        return images
    
if HAS_GDATA_PACKAGE_INSTALLED:
    AddGalleryType(PicasaGallery)