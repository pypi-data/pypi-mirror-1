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

class GalleryView(BrowserView):
    
    template = ViewPageTemplateFile('gallery.pt')
    
    def __init__(self, arg1, arg2):
        BrowserView.__init__(self, arg1, arg2)
    
    def __call__(self):
        return self.template()
    
    @memoize
    def images(self):
        return self.context.images()

    @memoize 
    def needsJQueryAdded(self):
        #3.0 doesn't include jquery by default
        portal_js_tool = getToolByName(self, 'portal_javascripts')
        return 'jquery.js' not in [c.getId() for c in portal_js_tool.getResources() if c.getEnabled()]            
        
        #mt = getToolByName(self, 'portal_migration')
        #return mt.getInstanceVersion().startswith('3.0')
        
    @memoize
    def firstpage(self):

        #temp hack since for IE6 and opera, my custom kss action does not work...
        if self.request['HTTP_USER_AGENT'].find('MSIE 6') > -1 or self.request['HTTP_USER_AGENT'].find('Opera') > -1:
            return self.images()
        else:
            return self.context.getPage(0)
        
    
class GalleryKSS(PloneKSSView):
    implements(IPloneKSSView)
    
    @kssaction
    def loadImagePage(self, page):
        ksscore = self.getCommandSet('core')
        kssgallery = self.getCommandSet('plone-true-gallery')

        images = [i.dict() for i in self.context.getPage(page)]
        
        doneLoading = "False"
        if len(images) == 0:
            doneLoading = "True"
        
        kssgallery.addImages(ksscore.getSameNodeSelector(), simplejson.dumps(images, separators=(',',':')), doneLoading, page)
    