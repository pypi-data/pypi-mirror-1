from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from Acquisition import aq_inner

class GalleryView(BrowserView):
    
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
        return [g.getObject() for g in aq_inner(self.context).getFolderContents() if g.meta_type == "SubGallery"]
        
    @memoize
    def images(self, gallery=None):
        if not gallery:
            gallery = self.context
        
        return gallery.images()
        
        
class SubGalleryView(BrowserView):

    template = ViewPageTemplateFile('subgallery.pt')

    def __call__(self):
        self.hasError = False
        return self.template()
        
    @memoize
    def images(self):
        return aq_inner(self.context).images()