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

HAS_GDATA_PACKAGE_INSTALLED = True

try:
    import gdata.photos.service
    import gdata.media
    import gdata.geo
    from gdata.photos.service import GooglePhotosException
except:
    HAS_GDATA_PACKAGE_INSTALLED = False

schema = Schema((
    StringField(
        name="picasaUsername",
        widget=StringField._properties['widget'](
            label="Email address of who this album belongs to"
        ),
        schemata="picasa"
    ),
    StringField(
        name="picasaPassword",
        widget=PasswordWidget(
            label="Password",
            description="Only required if your album is not public"
        ),
        schemata="picasa"
    ),
    BooleanField(
        name="isPicasaPrivate",
        widget=BooleanField._properties['widget'](
            label="Is this a private album?",
            description="Password is required if it is."
        ),
        default=False,
        schemata="picasa"
    ),
    StringField(
        name="picasaAlbum",
        widget=StringField._properties['widget'](
            label="Album",
            description="Name of your picasa web album.  To not use a picasa web album, just leave this blank."
        ),
        schemata="picasa"
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
    
    def __init__(self, gallery=None):
        self._gallery = gallery
    
    def name(self):
        return "Picasa"
    
    def description(self):
        return "A Gallery That Uses Picasa Web Albums"
    
    def getSchema(self):
        return self._schema.copy()
        
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
            return gd_client.GetFeed('/data/feed/api/user/%s/album/%s?kind=photo&imgmax=%s' % 
                (self._gallery.getPicasaUsername(), self._gallery.getPicasaAlbum(), self._gallery.image_size))
        except GooglePhotosException:
            #Do not show anything if connection failed
            return None
            
    def images(self):
        picasaGallery = self.feed()
        images = [self.assembleImageInfo(i) for i in picasaGallery.entry]
        if images is None:
            self._gallery.error = True
            self._gallery.errorMsg = "Could not connect to album %s" % self._gallery.getPicasaAlbum()
            
        return images
        
    def validate(self, value, *args, **kwargs):

        gallery = kwargs['instance']
        req = kwargs['REQUEST']
        album = value
        password = req.get('picasaPassword')
        username = req.get('picasaUsername')
        private = req.get('isPicasaPrivate')

        if len(password) == 0:
            password = gallery.getPicasaPassword()
        else:
            #hack, but for some reason the password value is lost on edits...
            gallery.picasa_password = password

        if private:
            if len(password) == 0 and len(gallery.getPicasaPassword()) == 0:
                if len(gallery.picasa_password) == 0:
                    return ("You must enter a password if the album if private.")
                else:
                    #continuation of the hack needed to keep the password on hand and not make the user re-enter every time
                    password = gallery.picasa_password
                    gallery.setPicasaPassword(password)

            try:
                gd_client = gdata.photos.service.PhotosService()
                gd_client.email = username
                gd_client.password = password
                gd_client.ProgrammaticLogin()

                gd_client.GetFeed('/data/feed/api/user/%s/album/%s?kind=photo' % (username, album))
                return 1
            except:
                return ("Error, you entered in the wrong information to connect to this album.  Please revise...")
        else:
            try:
                gd_client = gdata.photos.service.PhotosService()

                gd_client.GetFeed('/data/feed/api/user/%s/album/%s?kind=photo' % (username, album))
                return 1
            except:
                return ("Error, you entered in the wrong information to connect to album")
    
    
if HAS_GDATA_PACKAGE_INSTALLED:
    AddGalleryType(PicasaGallery)