from Products.CMFCore.utils import getToolByName

def install(context):
    
    if not context.readDataFile('collective.plonetruegallery.txt'):
        return
    
    
def uninstall(context):
    if not context.readDataFile('collective.plonetruegallery.uninstall.txt'):
        return
        
    portal = context.getSite()
    portal_actions = getToolByName(portal, 'portal_actions')
    object_buttons = portal_actions.object

    actions_to_remove = ('gallery_settings', 'refresh-gallery')
    for action in actions_to_remove:
        if action in object_buttons.objectIds():
            object_buttons.manage_delObjects([action])
            
