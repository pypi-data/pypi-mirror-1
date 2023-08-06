from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from collective.plonetruegallery.utils import getGalleryAdapter, getDisplayAdapter
from Products.CMFCore.utils import getToolByName

class GalleryView(BrowserView):
    
    subgallery_template = ViewPageTemplateFile('subgallery.pt')
    classic_template = ViewPageTemplateFile('classic.pt')
    slideshow_template = ViewPageTemplateFile('slideshow.pt')
        
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.adapter = getGalleryAdapter(self.context)
        self.displayer = getDisplayAdapter(self.context)
    
    def __call__(self):
        return getattr(self, self.displayer.name + "_template")()
        
    @memoize
    def firstpage(self):
        return self.adapter.get_page(0)
        
    def getAdaptedGallery(self, gallery):
        return getGalleryAdapter(gallery)

    
class GalleryAJAX(BrowserView):
    
    def loadImagePage(self):

        adapter = getGalleryAdapter(self.context)
        page = int(self.request.get('page', 1))
        images = adapter.get_page(page)
        
        doneLoading = "False"
        
        if len(images) == 0:
            doneLoading = "True"
        
        response = {
            'images' : images,
            'doneLoading': doneLoading,
            'page': page
        }

        return str(response)
    
class ForceCookingOfImages(BrowserView):
    
    def __call__(self):
        adapter = getGalleryAdapter(self.context)
        adapter.cook()
        
        self.request.response.redirect(self.context.absolute_url())
        
class ForceCookingOfAllGalleries(BrowserView):
    
    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        for gallery in catalog.searchResults(portal_type="Gallery"):
            gallery = gallery.getObject()
            
            self.request.response.write("cooking %s, located at %s\n" % (gallery.Title(), gallery.absolute_url()))
            
            adapter = getGalleryAdapter(gallery)
            adapter.cook()
            
        self.request.response.write("Timer is up!  Finished cooking!")
        