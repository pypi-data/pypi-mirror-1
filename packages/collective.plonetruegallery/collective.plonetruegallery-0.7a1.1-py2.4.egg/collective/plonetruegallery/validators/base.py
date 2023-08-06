from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

class BaseGalleryTypeValidator:
    __implements__ = IValidator
    
    def __init__(self, name="BaseGalleryTypeValidator", title='', description='', showError=True):
        self.name = name
        self.title = title or name
        self.description = description
        self.showError = showError
        
    def __call__(self, value, **kwargs):
        return True