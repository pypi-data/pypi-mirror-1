

class GalleryImageInfo:
    """
    Basic image information needed for smooth gallery
    """
    image_url = None
    thumb_url = None
    link = None
    title = ""
    description = ""
    width = None
    height = None
    
    def __init__(self, image_url=None, thumb_url=None, link=None, title="", description="", width=None, height=None):
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.link = link
        self.title = title
        self.description = description
        self.width = width
        self.height = height
        