from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

def import_various(context):
    
    if not context.readDataFile('uwosh.plonetruegallery.txt'):
        return
        
    site = context.getSite()
    portal_js_tool = site.portal_javascripts
    
    # check if jquery is installed.  If it isn't, add it to portal_javascripts
    # mostly for plone 3.0 compatability
    all_resources = portal_js_tool.getResources()
    possible_jquery_includes = [
        '++resource++jquery.js', 
        '++resource++jquery-1.2.6.js', 
        '++resource++jquery-1.2.6.pack.js'
    ]
    regular_jquery = [c.getId() for c in all_resources if c.getEnabled() and 'jquery.js' == c.getId()]
    
    if len(regular_jquery) == 0:
        # alright, so they don't have jquery, check if any other jquery is enabled
        # if it isn't, enable it!
        my_jquery = [c for c in all_resources if not c.getEnabled() and c.getId() in possible_jquery_includes]
        
        if len(my_jquery) == 1:
            my_jquery[0].setEnabled(True)
        
        
  