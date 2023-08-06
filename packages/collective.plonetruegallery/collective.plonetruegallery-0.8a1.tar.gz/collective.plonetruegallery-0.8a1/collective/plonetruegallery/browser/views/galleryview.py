from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from collective.plonetruegallery.utils import getGalleryAdapter, getDisplayAdapter
from Products.CMFCore.utils import getToolByName
from collective.plonetruegallery.settings import GallerySettings

class GalleryView(BrowserView):

    subgallery_template = ViewPageTemplateFile('subgallery.pt')

    def __call__(self):
        self.adapter = getGalleryAdapter(self.context, self.request)
        self.displayer = getDisplayAdapter(self.adapter)
        self.settings = GallerySettings(
            self.context,
            interfaces=[self.adapter.schema, self.displayer.schema]
        )
        return self.displayer.template(self, self.adapter, self.displayer, self.settings)
                
    @memoize
    def show_subgalleries(self):
        return self.adapter.settings.show_subgalleries and \
            self.adapter.contains_sub_galleries
        
    def getAdaptedGallery(self, gallery):
        return getGalleryAdapter(gallery, self.request)
        
class ForceCookingOfImages(BrowserView):
    
    def __call__(self):
        adapter = getGalleryAdapter(self.context, self.request)
        adapter.cook()
        
        self.request.response.redirect(self.context.absolute_url())
        
class ForceCookingOfAllGalleries(BrowserView):
    
    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        for gallery in catalog.searchResults(portal_type="Gallery"):
            gallery = gallery.getObject()
            
            self.request.response.write("cooking %s, located at %s\n" % (gallery.Title(), gallery.absolute_url()))
            
            adapter = getGalleryAdapter(gallery, self.request)
            adapter.cook()
            
        self.request.response.write("Timer is up!  Finished cooking!")
        
