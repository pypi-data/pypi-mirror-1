from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "collective.plonetruegallery"

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

ADD_CONTENT_PERMISSIONS = {
    'Gallery': 'collective.plonetruegallery: Modify Advanced Content',
}

setDefaultRoles('collective.plonetruegallery: Modify Advanced Content', ('Manager','Owner'))

product_globals = globals()

DEPENDENCIES = []

PRODUCT_DEPENDENCIES = []

FLICKR_API_VERSION = 1.2
GDATA_API_VERSION = "1.2.4"