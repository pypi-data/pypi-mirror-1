from collective.plonetruegallery.utils import getGalleryAdapter
                    
#checks if it has begun to use subgalleries
def object_added_to_gallery(subgallery, event):
    
    if event.newParent.meta_type == "Gallery":
        gallery = event.newParent
        gallery.contains_sub_gallery_objects = True
    
#checks if subgalleries have been removed
def object_removed_from_gallery(subgallery, event):
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
     
    