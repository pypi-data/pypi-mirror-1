

class GalleryImageInfo:
    
    image_url = None
    thumb_url = None
    link = None
    title = ""
    description = ""
    
    def __init__(self, image_url=None, thumb_url=None, link=None, title="", description=""):
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.link = link
        self.title = title
        self.description = description