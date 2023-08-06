from zope.interface import Interface

class IGalleryCommands(Interface):
    """The core commands"""

    def getNextImage():
        """from the current id, set the next image"""
        
    def getPreviousImage():
        """from the current id, set the next image"""
        
    def addImages(selector, images, doneLoading, page):
        """from the current id, set the next image"""
        
    def imageClicked(selector):
        """ """