from Products.CMFCore.utils import getToolByName
from utils import getGalleryAdapter

def import_various(context):
    
    if not context.readDataFile('uwosh.plonetruegallery.txt'):
        return
        
    site = context.getSite()
    portal_js_tool = site.portal_javascripts
    
    # check if jquery is installed.  If it isn't, add it to portal_javascripts
    # mostly for plone 3.0 compatability
    all_resources = portal_js_tool.getResources()
    regular_jquery = [c.getId() for c in all_resources if c.getEnabled() and 'jquery.js' == c.getId()]
    
    if len(regular_jquery) == 0:
        # alright, so they don't have jquery, check if any other jquery is enabled
        # if it isn't, enable it!
        my_jquery = [c for c in all_resources if not c.getEnabled() and c.getId() == '++resource++jquery.js']
        
        if len(my_jquery) > 0:
            my_jquery[0].setEnabled(True)
        
        
    catalog = getToolByName(site, 'portal_catalog')
    
    galleries = catalog.searchResults(portal_type="Gallery")
    
    for gallery in galleries:
        gallery = gallery.getObject()
        
        if not hasattr(gallery, 'last_cooked_time_in_minutes') or not hasattr(gallery, 'cooked_images'):
            gallery.last_cooked_time_in_minutes = 0
            gallery.cooked_images = []
            gallery._p_changed = 1
            getGalleryAdapter(gallery).cook()
    