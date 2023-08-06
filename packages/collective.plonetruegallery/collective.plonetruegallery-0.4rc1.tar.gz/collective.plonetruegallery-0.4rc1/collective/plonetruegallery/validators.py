from Products.validation.interfaces.IValidator import IValidator
import gdata.photos.service
import gdata.media
import gdata.geo

class isValidAlbumValidator:
    __implements__ = IValidator
    def __init__(self, name, title='', description='', showError=True):
        self.name = name
        self.title = title or name
        self.description = description
        self.showError = showError
        
    def __call__(self, value, *args, **kwargs):

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