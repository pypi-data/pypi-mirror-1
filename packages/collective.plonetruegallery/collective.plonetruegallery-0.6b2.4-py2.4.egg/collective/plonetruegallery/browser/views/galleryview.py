from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from Acquisition import aq_inner
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView
from kss.core import kssaction
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
import simplejson
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.interfaces import IGenerator

class GalleryView(BrowserView):
    
    template = ViewPageTemplateFile('gallery.pt')
    
    def __init__(self, arg1, arg2):
        BrowserView.__init__(self, arg1, arg2)
        self.adapter = getGalleryAdapter(self.context)
        self.generator = IGenerator(self.context)
    
    def __call__(self):
        return self.template()
    
    @memoize
    def images(self):
        return self.adapter.images()

    @memoize 
    def needsJQueryAdded(self):
        #3.0 doesn't include jquery by default
        portal_js_tool = getToolByName(self, 'portal_javascripts')
        return 'jquery.js' not in [c.getId() for c in portal_js_tool.getResources() if c.getEnabled()]
        
    @memoize
    def firstpage(self):

        # temp hack since for IE6 and opera, my custom kss action does not work...
        # switching over to use regular ajax may have fixed this..
        #if 'MSIE 6' in self.request['HTTP_USER_AGENT'] or 'Opera' in self.request['HTTP_USER_AGENT']:
        #    return self.adapter.images()
        #else:
        return self.adapter.getPage(0)
        
    
class GalleryKSS(BrowserView):
    implements(IPloneKSSView)
    
    def loadImagePage(self):

        adapter = getGalleryAdapter(self.context)
        page = int(self.request.get('page', 1))
        images = [i.dict() for i in adapter.getPage(page)]
        
        doneLoading = "False"
        
        if len(images) == 0:
            doneLoading = "True"
        
        response = {
            'images' : images,
            'doneLoading': doneLoading,
            'page': page
        }

        return simplejson.dumps(response, separators=(',',':'))
    