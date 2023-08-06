

class GalleryImageInfo:
    """
    Basic image information needed for smooth gallery
    """
    
    
    def __init__(self, image_url=None, thumb_url=None, link=None, title="", description=""):
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.link = link
        self.title = title
        self.description = description
    
    def dict(self):
        return {
            'image_url': self.image_url,
            'thumb_url': self.thumb_url,
            'link': self.link,
            'title': self.title,
            'description': self.description
        }