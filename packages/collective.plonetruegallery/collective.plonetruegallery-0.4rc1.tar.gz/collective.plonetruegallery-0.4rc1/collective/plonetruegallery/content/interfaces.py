from zope.interface import Interface

class IBaseGallery(Interface):
        
    def getImageUrl(self, image, subGallery=None):
        pass
        
    def getThumbUrl(self, image, subGallery=None):
        pass
        
    def getImageInfoDict(self, image):
        pass
    

class IGallery(Interface):
    """Gallery marker interface
    """
    def generateJavascript(self):
        pass

    def generateCSS(self):
        pass
    
    def containsSubGalleries(self):
        pass
        
    def getGalleryType(self):
        pass
    
class ISubGallery(IGallery):
    """Gallery marker interface
    """