from Products.validation.interfaces.IValidator import IValidator
from base import BaseGalleryTypeValidator
from collective.plonetruegallery.utils import getGalleryAdapter, PTGMessageFactory as _
from collective.plonetruegallery.interfaces import IFlickrAdapter

class ValidateFlickrUsername(BaseGalleryTypeValidator):
        
    def __call__(self, username, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        
        adapter = IFlickrAdapter(gallery)
        if req.get('type') == adapter.name:
            
            if len(username) == 0:
                return _(u"label_validate_flickr_specify_username", 
                    default=u"Flickr Error: You must specify a username.")
            
            try:
                gallery.flickr_userid = adapter.get_flickr_user_id(username)
                if gallery.flickr_userid is None:
                    return _(u"label_validate_flickr_user", default=u"Flickr Error: Could not validate flickr user.")
            except:
                return _(u"label_validate_flickr_user", default=u"Flickr Error: Could not validate flickr user.")

        return True


class ValidateFlickrSet(BaseGalleryTypeValidator):
    
    def __call__(self, photoset, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        adapter = IFlickrAdapter(gallery)

        if req.get('type') == adapter.name:
            
            if len(photoset) == 0:
                return _(u"label_validate_flickr_specify_user", default=u"Flickr Error: You must specify a flickr set to use.")
            
            try:
                userid = adapter.get_flickr_user_id(req.get('flickrUsername'))
                gallery.flickr_photosetid = adapter.get_flickr_photoset_id(photoset, userid)

                if gallery.flickr_photosetid is None:
                    return _(u"label_validate_flickr_find_set", default="Flickr Error: Could not find flickr set.")
            except:
                return _(u"label_validate_flickr_find_set", default="Flickr Error: Could not find flickr set.")

        return True