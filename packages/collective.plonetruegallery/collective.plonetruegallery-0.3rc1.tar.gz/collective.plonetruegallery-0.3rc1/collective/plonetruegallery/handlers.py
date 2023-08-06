from Products.ATContentTypes.content.image import ATImageSchema

"""
These are defined so that you won't need to check every time you
render a gallery if it has sub galleries in it or not and it also
checks for what size to render the images at on each edit so it 
doesn't need to be done on every page render
"""

picasa_sizes = (200, 288, 320, 400, 512, 576, 640, 720, 800)
image_sizes  = ATImageSchema['image'].sizes

def gallery_initialized(gallery, event):
    check_image_sizes(gallery)
    
def gallery_edited(gallery, event):
    check_image_sizes(gallery)
    
def check_image_sizes(gallery):
    
    #to automatically get the right sizes for the images
    if len(gallery.getPicasaAlbum()) == 0:
        #must start small so correct size is used...
        gallery.image_size = "mini"
        for size in image_sizes:
            if image_sizes[size][0] <= gallery.getWidth() or image_sizes[size][0] <= gallery.getHeight():
                if image_sizes[size][0] > image_sizes[gallery.image_size][0]:
                    gallery.image_size = size
    else:
        gallery.image_size = picasa_sizes[0]
        for size in picasa_sizes:
            if size <= gallery.getWidth() or size <= gallery.getHeight():
                if size > gallery.image_size:
                    gallery.image_size = size
                    
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
                if gallery[id].meta_type == "SubGallery":
                    gallery.contains_sub_gallery_objects = True
                    break
                else:
                    gallery.contains_sub_gallery_objects = False
        else:
            gallery.contains_sub_gallery_objects = False
     
    