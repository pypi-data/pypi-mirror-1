from collective.plonetruegallery.utils import getGalleryAdapter
from utils import getGalleryAdapter

def gallery_modified(gallery, event):
    """
    addition, removal or reordering of sub-objects
    """ 
    contents_ids = gallery.objectIds()
    
    if len(contents_ids) > 0:
        for id in contents_ids:
            if gallery[id].meta_type == "Gallery":
                gallery.contains_sub_gallery_objects = True
                break
            else:
                gallery.contains_sub_gallery_objects = False
    else:
        gallery.contains_sub_gallery_objects = False
            
    adapter = getGalleryAdapter(gallery)
    adapter.cook()

def gallery_edited(gallery, event):
    """
    """
    adapter = getGalleryAdapter(gallery)
    adapter.cook()
    
def image_edited(image, event):
    """
    """
    
    if image.getParentNode().portal_type == 'Gallery':
        adapter = getGalleryAdapter(image.getParentNode())
        adapter.cook()
