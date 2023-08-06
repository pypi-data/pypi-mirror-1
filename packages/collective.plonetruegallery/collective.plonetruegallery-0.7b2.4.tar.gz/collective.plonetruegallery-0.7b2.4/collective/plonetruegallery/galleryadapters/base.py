from collective.plonetruegallery.utils import PTGMessageFactory as _
import time
from collective.plonetruegallery.content.config import PAGE_SIZE
from collective.plonetruegallery.interfaces import IBaseGalleryAdapter
from zLOG import LOG, INFO
import random
from zope.interface import implements
from zope.component import adapts


class BaseAdapter(object):
    
    implements(IBaseGalleryAdapter)
    
    sizes = {}
    schema =  None
    
    name = u"base"
    description = _(u"label_base_gallery_type", default=u"base: this isn't actually a gallery type.  Think abstract class here..." )
    
    cook_delay = 1440 #will update once a day
    
    def __init__(self, gallery):
        self.gallery = gallery

        if self.time_to_cook():
            self.cook()
    
    def time_to_cook(self):
        return (self.gallery.last_cooked_time_in_minutes + self.cook_delay) < (time.time()/60)
    
    def log_error(self, ex='', inst='', msg=""):
        LOG('collective.plonetruegallery', INFO, "%s adapter, gallery is %s\n%s\n%s\n%s" % 
            (self.name, str(self.gallery), msg, ex, inst))
            
    def cook(self):
        self.gallery.cooked_images = self.retrieve_images()
        self.gallery.last_cooked_time_in_minutes = time.time()/60
        self.gallery._p_changed = 1
        
    def get_page(self, page, page_size=PAGE_SIZE):
        start = page_size*page
        end = (page_size*page) + page_size

        return self.gallery.cooked_images[start:end]
        
    def get_first_image(self):

        if len(self.gallery.cooked_images) > 0:
            return self.gallery.cooked_images[0]
        else:
            return None
      
    def get_random_image(self):
        
        if len(self.gallery.cooked_images) > 0:
            return self.gallery.cooked_images[random.randint(0, self.number_of_images()-1)]
        else:
            return {}
            
    def assemble_image_information(self, image):
        raise Exception("Not implemented")
            
    def number_of_images(self):
        return len(self.gallery.cooked_images)
        
    def retrieve_images(self):
        raise Exception("Not implemented")
        
    def get_all_cooked_images(self):
        return self.gallery.cooked_images