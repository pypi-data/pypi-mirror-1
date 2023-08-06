from zope.interface import implements
from zope.interface import Interface, Attribute

class IBaseGalleryAdapter(Interface):
    sizes = Attribute("""image size mappings for the gallery type""")
    schema =  Attribute("""Schema of gallery specific""")
    
    name = Attribute("""Name of the gallery""")
    description = Attribute("Description of gallery type")
    cook_delay = Attribute("""Time between updates of gallery images.  
        This update of images can be forced by appending refresh on a gallery.""")

    def cook(self):
        """
        this will make it so the gallery's images are not aggregated every
        single time the gallery is displayed.
        """

    def get_random_image():
        """"""

    def retrieve_images():
        """
        This method retrieves all the images to be cooked
        """
        
    def get_page(page, page_size):
        """
        """
        
    def get_first_image():
        """"""
            
    def number_of_images():
        """"""
        
    def get_all_images():
        """
        returns all the cooked images for the gallery
        """

    def assemble_image_information():
        """"""

class IBasicAdapter(IBaseGalleryAdapter):
    """
    nothing special
    """
        
    def get_image_url(image):
        """
        takes an image and create the url for it
        """

    def get_thumb_url(image):
        """
        returns the thumbnail url for an image
        """
    
class IFlickrAdapter(IBaseGalleryAdapter):
    """
    """
    
    def get_flickr_user_id(username):
        """
        returns the actual user id of someone given a username
        """
        
    def get_flickr_photoset_id(theset, userid=None):
        """
        returns the photoset id given a set name and user id
        """

    def get_mini_photo_url(photo):
        """
        takes a photo and creates the photo url
        """
        
    def get_photo_link(photo):
        """
        creates the photo link url
        """
        
    def get_large_photo_url(photo):
        """
        create the large photo url
        """
        
    def flickr():
        """
        returns a flickrapi object for the api key
        """
        
class IPicasaAdapter(IBaseGalleryAdapter):
    """
    """
    
    gd_client = Attribute("property for gd_client instance")
        
    def authenticate_picasa():
        """
        authenticates with picasa using username and password
        """
        
    def get_album_name():
        """
        returns the selected album name
        """
        
    def feed():
        """
        returns the picasa feed for the given album
        """
        
class IDisplayType(Interface):
    
    name = Attribute("""name of display type""")
    description = Attribute("""description of type""")
    template = Attribute("""The template used to render the gallery""")
    
    def css():
        """
        Specific css that is generated for that display type
        """
        
    def javascript():
        """
        specific javascript that is generated for the display type
        """
        
class IClassicDisplayType(IDisplayType):
    """
    The old-school way of displaying the gallery
    """
    
class ISlideshowDisplayType(IDisplayType):
    """
    using Slideshow 2 to display the gallery
    """
    
    def image_data():
        """
        assembles the image data to be set for the javascript
        """
    
    