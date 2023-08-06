
from zope.interface import Interface, Attribute

class IBasicGalleryTypeValidator(Interface):
    """"""

class IGenerator(Interface):
    """
    responsible for generating css and javascript for gallery
    """
    
    def css(self):
        """"""
    
    def javascript(self):
        """"""

class IGalleryAdapter(Interface):
    image_sizes = Attribute("""Potential sizes for gallery""")
    schema =  Attribute("""Schema of gallery specific""")
    
    name = Attribute("""Name of the gallery""")
    description = Attribute("Description of gallery type")
        
    def info(self):
        """
        return information on the gallery
        """

    def getWidth(self):
        """"""

    def getHeight(self):
        """"""

    def getThumbnailWidth(self):
        """
        returns the width of a thumbnail
        """
        
    def getThumbnailHeight(self):
        """
        """
            
    def numberOfImages(self):
        """
        """
        
    def getFirstImage(self):
        """
        """
        
    def images(self):
        """
        return all images
        """

    def getPage(self, page):
        """
        get first page of images
        """

class IBasicAdapter(IGalleryAdapter):
    """
    nothing special
    """
    def getImageUrl(self, image, subGallery=None):
        """
        """

    def getThumbUrl(self, image, subGallery=None):
        """
        """

    def assembleImageInfo(self, image):
        """
        """
    
class IFlickrAdapter(IBasicAdapter):
    """
    """
    
    def flickr(self):
        """
        returns flickr api instance
        """
    def getMiniPhotoURL(self, photo):
        """
        """

    def getPhotoLink(self, photo):
        """
        """

    def getLargePhotoURL(self, photo):
        """"""
        
    def getSetUrl(self):
        """"""

    def getSlideshowUrl(self):
        """"""

    def getFlickrUserid(self, username):
        """"""

    def getCount(self):
        """"""

    def getFlickrPhotosetId(self, theset, userid=None):
        """
        """
        
class IPicasaAdapter(IBasicAdapter):
    """
    """
    def authenticatePicasa(self, gd_client):
        """
        """
        
    def feed(self):
        """
        get the picasa feed
        """