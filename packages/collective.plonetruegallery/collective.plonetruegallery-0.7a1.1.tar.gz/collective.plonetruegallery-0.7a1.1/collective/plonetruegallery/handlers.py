from collective.plonetruegallery.utils import getGalleryAdapter
from utils import getGalleryAdapter


def object_added_to_gallery(subgallery, event):
    """
    Checks it if has begun to use sub-galleries
    """
    if event.newParent.meta_type == "Gallery":
        gallery = event.newParent
        gallery.contains_sub_gallery_objects = True
    else:
        adapter = getGalleryAdapter(gallery)
        adapter.cook()
    

def object_removed_from_gallery(subgallery, event):
    """
    This checks if subgalleries or images have been removed...
    """
    if event.oldParent.meta_type == "Gallery":
        gallery = event.oldParent
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
    else:
        adapter = getGalleryAdapter(gallery)
        adapter.cook()
     

def gallery_edited(gallery, event):
    """
    Things that need to happen when a gallery is edited
        1. re-cook all images
    """
    adapter = getGalleryAdapter(gallery)
    adapter.cook()
    
