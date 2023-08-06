from Products.validation.interfaces.IValidator import IValidator
from base import BaseGalleryTypeValidator
from collective.plonetruegallery.utils import getGalleryAdapter
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
                return ("Picasa Error: You must specify a picasa username with the '@gmail.com'")
            
        return True

class ValidatePicasaPassword(BaseGalleryTypeValidator):
        
    def __call__(self, password, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        
        adapter = getGalleryAdapter(gallery)
        
        if req.get('type') == adapter.name and req.get('isPicasaPrivate'):
            try:
                gd_client = adapater.gd_client
                gd_client.email = req.get('picasaUsername')
                gd_client.password = password
                gd_client.ProgrammaticLogin()
            except:
                return ("Picasa Error: Incorrect username or password.")

        return True
        
class ValidateIsPicasaPrivate(BaseGalleryTypeValidator):

    def __call__(self, private, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        adapter = getGalleryAdapter(gallery)

        if req.get('type') == adapter.name and private:
            new_password = req.get('picasaPassword')
            
            if len(new_password) == 0:
                return ("Picasa Error: You must enter a password if it is a private album.")

        return True
        
class ValidatePicasaAlbum(BaseGalleryTypeValidator):

    def __call__(self, album, **kwargs):
        req = kwargs['REQUEST']
        gallery = kwargs['instance']
        adapter = getGalleryAdapter(gallery)

        if req.get('type') == adapter.name:
            
            try:
                gd_client = adapter.gd_client
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
                return ("Picasa Error: Could not find album.")

            return ("Picasa Error: Could not find album.")

        return True