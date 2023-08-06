import gdata.photos.service
import gdata.media
import gdata.geo
from gdata.photos.service import GooglePhotosException
from urllib import urlopen

PICASA_USERNAME = "vangheem@gmail.com"
PICASA_ALBUM = "DellsOfEauClaire"
FLICKR_USERNAME = "nathan.vangheem"
FLICKR_SET = "Lahaini, Hawaii"

def getPhotoURLs(amount=5):
    gd_client = gdata.photos.service.PhotosService()
    url = '/data/feed/api/user/%s/album/%s?kind=photo&imgmax=%s' % (
        PICASA_USERNAME, 
        PICASA_ALBUM, 
        200,
    )
    feed = gd_client.GetFeed(url)
    
    return [image.content.src for image in feed.entry[0:amount]]
    
def addSomePhotosToGallery(gallery):
    
    for image_url in getPhotoURLs():
        
        image_data = urlopen(image_url).read()
        id = gallery.generateUniqueId()
        gallery.invokeFactory("Image", id)
        
        image = gallery[id]
        
        image.setImage(image_data)
        
        
        
        
    