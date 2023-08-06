from collective.plonetruegallery.interfaces import IPicasaAdapter
from collective.plonetruegallery.content.interfaces import IGallery
from collective.plonetruegallery.schemas.picasa import PicasaSchema
from zope.interface import implements
from zope.component import adapts
from base import BaseAdapter
from collective.plonetruegallery.utils import PTGMessageFactory as _

try:
    import gdata.photos.service
    from gdata.photos.service import GooglePhotosException
except:
    pass

def add_condition():

    try:
        import gdata.photos.service
        from gdata.photos.service import GooglePhotosException
    except:
        return False

    return True

GDATA = {}

class PicasaAdapter(BaseAdapter):
    implements(IPicasaAdapter)
    
    schema = PicasaSchema
    name = u"picasa"
    description = _(u"label_picasa_gallery_type", 
        default=u"picasa: A Gallery That Uses a Picasa Web Album For its Images")
    
    sizes = {
        'small': {
            'width': 320,
            'height': 320
        },
        'medium':{
            'width': 576,
            'height': 576
        },
        'large':{
            'width': 800,
            'height': 800
        },
        'thumbnail' : {
            'width' : 72,
            'height' : 72
        }
    }
    
    def __init__(self, gallery):
        self.gallery = gallery
        
    def get_gd_client(self):
        if GDATA.has_key(self.gallery.UID()):
            return GDATA[self.gallery.UID()]
        else:
            self.gd_client = gdata.photos.service.PhotosService()
            return GDATA[self.gallery.UID()]
            
    def set_gd_client(self, value):
        GDATA[self.gallery.UID()] = value
        
    gd_client = property(get_gd_client, set_gd_client)
        
    def authenticate_picasa(self):
        gd_client = self.gd_client
        gd_client.email = self.gallery.getPicasaUsername()
        gd_client.password = self.gallery.getPicasaPassword()
        gd_client.ProgrammaticLogin()

    def assemble_image_information(self, image):
        return {
            'image_url' : image.content.src, 
            'thumb_url' : image.media.thumbnail[0].url,
            'link' : image.content.src,
            'title' : image.title.text,
            'description' : image.summary.text or ''
        }
        
    def get_album_name(self):
        feed = self.gd_client.GetUserFeed(user=self.gallery.getPicasaUsername())
        
        name = self.gallery.getPicasaAlbum()
        for entry in feed.entry:
            if entry.name.text == name or entry.title.text == name:
                return entry.name.text
                
        return None
        
    def feed(self):
        gd_client = self.gd_client
        if self.gallery.getIsPicasaPrivate():
            self.authenticate_picasa()

        try:
            url = '/data/feed/api/user/%s/album/%s?kind=photo&imgmax=%s&thumbsize=%sc' % (
                self.gallery.getPicasaUsername(), 
                self.get_album_name(), 
                self.sizes[self.gallery.getSize()]['width'],
                self.sizes['thumbnail']['width']
            )
            feed = gd_client.GetFeed(url)
            return feed
        except GooglePhotosException, inst:
            #Do not show anything if connection failed
            self.log_error(GooglePhotosException, inst, "Error getting photo feed")
            return None
        
    def retrieve_images(self):
        try:
            picasaGallery = self.feed()
            images = [self.assemble_image_information(i) for i in picasaGallery.entry]
            return images
        except GooglePhotosException, inst:
            self.log_error(GooglePhotosException, inst, "Error getting all images")
            return []
            