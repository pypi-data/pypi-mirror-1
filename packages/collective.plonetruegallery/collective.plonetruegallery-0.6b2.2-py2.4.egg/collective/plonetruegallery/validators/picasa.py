from Products.validation.interfaces.IValidator import IValidator
from base import BaseGalleryTypeValidator
from collective.plonetruegallery.utils import getGalleryAdapter, PTGMessageFactory as _
from collective.plonetruegallery.interfaces import IPicasaAdapter

try:
    import gdata.photos.service
    import gdata.media
    import gdata.geo
    from gdata.photos.service import GooglePhotosException
except:
    pass

class ValidatePicasaUsername(BaseGalleryTypeValidator):

    def __call__(self, username, **kwargs):
        req = kwargs['REQUEST']

        if req.get('type') == 'picasa':
            if "@gmail.com" not in username:
                return _(u"label_validate_picasa_specify_username", 
                    default=u"Picasa Error: You must specify a picasa username with the '@gmail.com'")
            
        return True

class ValidatePicasaPassword(BaseGalleryTypeValidator):
        
    def __call__(self, password, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']        
        adapter = IPicasaAdapter(gallery)

        if req.get('type') == adapter.name and req.get('isPicasaPrivate'):
            
            if len(password) == 0:
                return _(u"label_validate_picasa_enter_password", 
                    default=u"Picasa Error: You must enter a password if it is a private album.")
            
            try:
                gd_client = adapter.gd_client
                gd_client.email = req.get('picasaUsername')
                gd_client.password = password
                gd_client.ProgrammaticLogin()
            except:
                return _(u"label_validate_picasa_incorrect_password", 
                    default=u"Picasa Error: Incorrect username or password.")

        return True
        
class ValidateIsPicasaPrivate(BaseGalleryTypeValidator):

    def __call__(self, private, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        adapter = IPicasaAdapter(gallery)

        if req.get('type') == adapter.name and private:
            new_password = req.get('picasaPassword')
            
            if len(new_password) == 0:
                return _(u"label_validate_picasa_enter_password", 
                    default=u"Picasa Error: You must enter a password if it is a private album.")

        return True
        
class ValidatePicasaAlbum(BaseGalleryTypeValidator):

    def __call__(self, album, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        adapter = IPicasaAdapter(gallery)

        if req.get('type') == adapter.name:
            
            try:
                gd_client = adapter.gd_client
                gd_client.email = req.get('picasaUsername')
            
                if req.get('isPicasaPrivate'):
                    password = req.get('picasaPassword')
                    if len(password) == 0:
                        return _(u"label_validate_picasa_enter_password", 
                            default=u"Picasa Error: You must enter a password if it is a private album.")
                    gd_client.password = password
                    gd_client.ProgrammaticLogin()
                
                feed = gd_client.GetUserFeed(user=req.get('picasaUsername'))
                for entry in feed.entry:
                    if entry.title.text == album or entry.name.text == album:
                        return True
            except:
                return _(u"label_validate_picasa_find_album", 
                    default=u"Picasa Error: Could not find album.")

            return _(u"label_validate_picasa_find_album", 
                default=u"Picasa Error: Could not find album.")

        return True