from collective.plonetruegallery.interfaces import IPicasaAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from collective.plonetruegallery.content.galleryimageinfo import GalleryImageInfo
from collective.plonetruegallery.schemas.picasa import PicasaSchema
from zope.interface import implements
from zope.component import adapts
from collective.plonetruegallery.galleryadapters.basic import BasicAdapter
from collective.plonetruegallery.content.config import PAGE_SIZE
from collective.plonetruegallery.utils import RegisterGalleryType
from zLOG import LOG, INFO

HAS_GDATA_PACKAGE_INSTALLED = True

try:
    import gdata.photos.service
    import gdata.media
    import gdata.geo
    from gdata.photos.service import GooglePhotosException
except:
    HAS_GDATA_PACKAGE_INSTALLED = False

NAME = 'picasa'
DESCRIPTION = "A Gallery That Uses a Picasa Web Album For its Images"

GDATA = {}

class PicasaAdapter(object):
    implements(IPicasaAdapter)
    adapts(IGallery)
    
    schema = PicasaSchema
    picasa_sizes = (200, 288, 320, 400, 512, 576, 640, 720, 800)
    name = NAME
    description = DESCRIPTION
    thumbnail_size = 72
    
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
    
    def setup(self):
        pass
    
    def getWidth(self):
        return self.sizes[self.gallery.getSize()]['width']
        
    def getHeight(self):
        return self.sizes[self.gallery.getSize()]['height']
    
    def __init__(self, gallery):
        self.gallery = gallery

    def getThumbnailWidth(self):
        return self.thumbnail_size

    def getThumbnailHeight(self):
        return self.thumbnail_size
        
    def info(self):
        feed = self.feed()
        return {
            'count': len(feed.entry),
            'contents_url': feed.GetHtmlLink().href
        }
        
    def get_gd_client(self):
        if GDATA.has_key(self.gallery.UID()):
            return GDATA[self.gallery.UID()]
        else:
            self.gd_client = gdata.photos.service.PhotosService()
            return GDATA[self.gallery.UID()]
            
    def set_gd_client(self, value):
        GDATA[self.gallery.UID()] = value
        
    gd_client = property(get_gd_client, set_gd_client)
        
    def authenticatePicasa(self):
        gd_client = self.gd_client
        gd_client.email = self.gallery.getPicasaUsername()
        gd_client.password = self.gallery.getPicasaPassword()
        gd_client.ProgrammaticLogin()

    def assembleImageInfo(self, image):
        return GalleryImageInfo(
            image_url = image.content.src, 
            thumb_url = image.media.thumbnail[0].url,
            link = image.content.src,
            title = image.title.text,
            description = image.summary.text 
        )
        
    def getAlbumName(self):
        feed = self.gd_client.GetUserFeed(user=self.gallery.getPicasaUsername())
        
        name = self.gallery.getPicasaAlbum()
        for entry in feed.entry:
            if entry.name.text == name or entry.title.text == name:
                return entry.name.text
                
        return None
        
    def feed(self):
        gd_client = self.gd_client
        if self.gallery.getIsPicasaPrivate():
            self.authenticatePicasa()

        try:
            url = '/data/feed/api/user/%s/album/%s?kind=photo&imgmax=%s&thumbsize=%sc' % (
                self.gallery.getPicasaUsername(), 
                self.getAlbumName(), 
                self.getWidth(),
                self.thumbnail_size
            )
            feed = gd_client.GetFeed(url)
            return feed
        except GooglePhotosException, inst:
            #Do not show anything if connection failed
            self.handleerror(GooglePhotosException, inst, "Error getting photo feed")
            return []
    
    def numberOfImages(self):
        try:
            picasaGallery = self.feed()
            return len(picasaGallery.entry)
        except GooglePhotosException, inst:
            # probably not the best idea to swallow errors here
            # I just don't want the user not to be able to change settings with clicks...
            self.handleerror(GooglePhotosException, inst, "Error getting number of images")
            return 0

    def getFirstImage(self):
        try:
            picasaGallery = self.feed()
            return self.assembleImageInfo(picasaGallery.entry[0])
        except Exception, inst:
            # again, not so sure about swallowing the errors...
            self.handleerror(Exception, inst, "Can't get first image")
            return None

    def handleerror(self, ex='', inst='', msg=""):
        """
        Manage exceptions somehow here..
        """
        LOG('collective.plonetruegallery', INFO, "picasa adapter, gallery is %s\n%s\n%s\n%s" % (str(self.gallery), msg, ex, inst) )
        

    def getPage(self, page):
        start = PAGE_SIZE*page
        end = (PAGE_SIZE*page) + PAGE_SIZE
        
        try:
            picasaGallery = self.feed()
            images = [self.assembleImageInfo(i) for i in picasaGallery.entry[start:end]]
            return images
        except GooglePhotosException, inst:
            self.handleerror(GooglePhotosException, inst, "Error getting first page")
        except Exception, inst:
            self.handleerror(Exception, inst, "Error getting first page")
    
        return []
        
    def images(self):
        try:
            picasaGallery = self.feed()
            images = [self.assembleImageInfo(i) for i in picasaGallery.entry]
            return images
        except GooglePhotosException, inst:
            self.handleerror(GooglePhotosException, inst, "Error getting all images")
            return []
            
if HAS_GDATA_PACKAGE_INSTALLED:
    RegisterGalleryType(NAME, DESCRIPTION, IPicasaAdapter, PicasaSchema)