from collective.plonetruegallery.interfaces import IPicasaAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from collective.plonetruegallery.content.galleryimageinfo import GalleryImageInfo
from collective.plonetruegallery.schemas.picasa import PicasaSchema
from zope.interface import implements
from zope.component import adapts
from collective.plonetruegallery.galleryadapters.basic import BasicAdapter
from collective.plonetruegallery.content.config import PAGE_SIZE
from collective.plonetruegallery.utils import RegisterGalleryType

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
        
    def authenticatePicasa(self, gd_client):
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
        
    def getAlbumName(self, gd):
        feed = gd.GetUserFeed()
        
        name = self.gallery.getPicasaAlbum()
        for entry in feed.entry:
            if entry.name.text == name or entry.title.text == name:
                return entry.name.text
        
    def feed(self):
        gd_client = gdata.photos.service.PhotosService()
        if self.gallery.getIsPicasaPrivate():
            self.authenticatePicasa(gd_client)

        try:
            url = '/data/feed/api/user/%s/album/%s?kind=photo&imgmax=%s&thumbsize=%sc' % (
                self.gallery.getPicasaUsername(), 
                self.getAlbumName(gd_client), 
                self.getWidth(),
                self.thumbnail_size
            )
            feed = gd_client.GetFeed(url)
            return feed
        except:
            #Do not show anything if connection failed
            return []
    
    def numberOfImages(self):
        try:
            picasaGallery = self.feed()
            return len(picasaGallery.entry)
        except:
            return 0

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
            self.gallery.error = True
            self.gallery.errorMsg = "Could not connect to album %s" % self.gallery.getPicasaAlbum()
            
        return images
            
if HAS_GDATA_PACKAGE_INSTALLED:
    RegisterGalleryType(NAME, DESCRIPTION, IPicasaAdapter, PicasaSchema)