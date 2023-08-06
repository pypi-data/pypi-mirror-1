from Products.validation.interfaces.IValidator import IValidator
from base import BaseGalleryTypeValidator
from collective.plonetruegallery.utils import getGalleryAdapter

class ValidateFlickrUsername(BaseGalleryTypeValidator):
        
    def __call__(self, username, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        
        adapter = getGalleryAdapter(gallery)
        
        if req.get('type') == adapter.name:
            try:
                gallery.flickr_userid = adapter.getFlickrUserid(username)
                if gallery.flickr_userid is None:
                    return ("Flickr Error: Could not validate flickr user.")
            except:
                return ("Flickr Error: Could not validate flickr user.")

        return True


class ValidateFlickrSet(BaseGalleryTypeValidator):
    
    def __call__(self, photoset, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        adapter = getGalleryAdapter(gallery)

        if req.get('type') == adapter.name:
            try:
                userid = adapter.getFlickrUserid(req.get('flickrUsername'))
                gallery.flickr_photosetid = adapter.getFlickrPhotosetId(photoset, userid)

                if gallery.flickr_photosetid is None:
                    return ("Flickr Error: Could not find flickr set.")
            except:
                return ("Flickr Error: Could not find flickr set.")

        return True