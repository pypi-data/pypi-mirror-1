from zope.interface import Interface
from zope.configuration.fields import GlobalObject, GlobalInterface
from zope.configuration.fields import Tokens, Path, Bool, PythonIdentifier
from zope.configuration.fields import MessageID
from zope.schema import Text, TextLine, Id
from zope.security.zcml import Permission
from zope.app.component.back35 import LayerField
from zope.app.publisher.browser.fields import MenuField
from zope.component import getGlobalSiteManager
from zope.app.publisher.browser.metadirectives import IPageDirective
from zope.component.zcml import IAdapterDirective, adapter as add_adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from collective.plonetruegallery.content.interfaces import IGallery
from collective.plonetruegallery.interfaces import IBaseGalleryAdapter, IDisplayType

GalleryTypes = []
DisplayTypes = []

class IBaseTypeDirective(Interface):
    condition = GlobalObject(
        title=u"Condition Method",
        description=u"Method that returns a boolean to check whether or not the adapter should be used",
        required=False
    )

class IGalleryTypeDirective(IAdapterDirective, IBaseTypeDirective):
    """
    """

    
class IDisplayTypeDirective(IBaseTypeDirective):
    """
    pretty much just a browser page... just have to do some extra work...
    """

    class_ = GlobalObject(
        title=u"The class of the display",
        description=u"",
        required=True
    )


def add_gallery_type(_context, factory, provides=IBaseGalleryAdapter, for_=[IGallery], 
                    permission=None, name='', trusted=False, locate=False, condition=None):

    if condition is not None and not condition():
        return
    
    if len(factory) != 1:
        raise Exception("Can only specify one factory")
    
    if not IBaseGalleryAdapter.implementedBy(factory[0]):
        raise Exception("factory must implement IBaseGalleryAdapter")
    
    GalleryTypes.append(factory[0])
    add_adapter(_context, factory, provides, for_, permission, name, trusted, locate)
    
def add_display_type(_context, class_, condition=None):

    if condition is not None and not condition():
        return

    if not IDisplayType.implementedBy(class_):
        raise Exception("Display class must implement IDisplayType")

    DisplayTypes.append(class_)

