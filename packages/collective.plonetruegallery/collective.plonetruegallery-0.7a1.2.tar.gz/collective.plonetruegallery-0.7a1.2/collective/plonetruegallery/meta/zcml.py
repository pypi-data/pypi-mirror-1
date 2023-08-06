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
from zope.app.publisher.browser.viewmeta import page as add_page
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

    
class IDisplayTypeDirective(IPageDirective, IBaseTypeDirective):
    """
    pretty much just a browser page... just have to do some extra work...
    """

    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False
        )
        
    name = TextLine(
        title=u"The name of the page that is the default.",
        description=u"""Used with normal browser pages, but not needed here..  So this is actually ignored""",
        required=False
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
    
def add_display_type(_context, for_=IGallery, name=None, permission="zope2.View",
             layer=IDefaultBrowserLayer, template=None, class_=None,
             allowed_interface=None, allowed_attributes=None,
             attribute='__call__', menu=None, title=None, condition=None
             ):

    if condition is not None and not condition():
        return

    DisplayTypes.append(class_)
    
    name = class_.name

    if not IDisplayType.implementedBy(class_):
        raise Exception("Display class must implement IDisplayType")
    
    add_page(_context, name, permission, for_, layer, template, class_,
            allowed_interface, allowed_attributes, attribute, menu, title)