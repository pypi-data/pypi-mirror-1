from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

import gdata.photos.service
import gdata.media
import gdata.geo
from gdata.photos.service import GooglePhotosException

class PicasaAlbum:
    
    def authenticatePicasa(self, gd_client, gallery):
        gd_client.email = gallery.getPicasaUsername()
        gd_client.password = gallery.getPicasaPassword()
        gd_client.ProgrammaticLogin()
        
    def getPicasaPhotos(self, gallery):
        gd_client = gdata.photos.service.PhotosService()
        if gallery.getIsPicasaPrivate():
            self.authenticatePicasa(gd_client, gallery)

        try:
            return gd_client.GetFeed('/data/feed/api/user/%s/album/%s?kind=photo&imgmax=%s' % (gallery.getPicasaUsername(), gallery.getPicasaAlbum(), gallery.image_size))
        except GooglePhotosException:
            #Do not show anything if connection failed
            return None
    
    def getImageInfoDict(self, image):
        return {   
            'image_url': image.content.src, 
            'thumb_url': image.media.thumbnail[0].url,
            'link': image.content.src,
            'title': image.title.text,
            'description': image.summary.text 
        }

class GalleryView(BrowserView, PicasaAlbum):
    
    template = ViewPageTemplateFile('gallery.pt')
    
    def __call__(self):
        self.hasError = False
        return self.template()
        
    @memoize
    def isGallerySet(self):
        return self.context.containsSubGalleries()
    
    @memoize
    def notGallerySet(self):
        return not self.context.containsSubGalleries()
        
    @memoize
    def galleries(self):
        return [g.getObject() for g in self.context.getFolderContents() if g.meta_type == "SubGallery"]
        
    @memoize
    def images(self, gallery=None):
        if not gallery:
            gallery = self.context
        
        if len(gallery.getPicasaAlbum()) > 0:
            picasaGallery = self.getPicasaPhotos(gallery)
            images = [self.getImageInfoDict(i) for i in picasaGallery.entry]
            if images is None:
                self.hasError = True
                self.errorMsg = "Could not connect to album %s" % gallery.getPicasaAlbum()
            else:
                return images
        else:
            return [gallery.getImageInfoDict(i) for i in self.context.getFolderContents() if i.meta_type == "ATImage"]
        
        
class SubGalleryView(BrowserView, PicasaAlbum):

    template = ViewPageTemplateFile('subgallery.pt')

    def __call__(self):
        self.hasError = False
        return self.template()
        
    @memoize
    def images(self):
        gallery = self.context
        
        if len(gallery.getPicasaAlbum()) > 0:
            picasaGallery = self.getPicasaPhotos(gallery)
            images = [self.getImageInfoDict(i) for i in picasaGallery.entry]
            if images is None:
                self.hasError = True
                self.errorMsg = "Could not connect to album %s" % gallery.getPicasaAlbum()
            else:
                return images
        else:
            return [gallery.getImageInfoDict(i) for i in self.context.getFolderContents() if i.meta_type == "ATImage"]