from collective.plonetruegallery.interfaces import IBasicAdapter, \
    IBasicGallerySettings, IImageInformationRetriever, IGalleryAdapter
from Products.ATContentTypes.content.image import ATImageSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getMultiAdapter, adapts
from base import BaseAdapter, BaseImageInformationRetriever
from collective.plonetruegallery import PTGMessageFactory as _
from Products.ATContentTypes.interface.image import IImageContent 
from OFS.interfaces import IObjectManager
from Products.ATContentTypes.interface.topic import IATTopic

class BasicAdapter(BaseAdapter):
    implements(IBasicAdapter, IGalleryAdapter)
    
    name = u"basic"
    description = _(u"label_default_gallery_type", 
        default=u"Use Plone To Manage Images")

    schema = IBasicGallerySettings
    cook_delay = 0
    
    size_map = {
		'small' : 'preview',
		'medium' : 'large',
		'large' : 'large'
	}

    # I know these sizes are not the natural sizes of the images, but
    # the normals sizes for the plone scaling are really too small to be
    # useful at all.
    sizes = {
        'small': {
            'width': 320,
            'height': 320
        },
        'medium':{
            'width': 576,
            'height': 576
        },
        'large':{
            'width': ATImageSchema['image'].sizes['large'][0],
            'height': ATImageSchema['image'].sizes['large'][1]
        },
        'thumbnail': {
            'width' : ATImageSchema['image'].sizes['tile'][0],
            'height' : ATImageSchema['image'].sizes['tile'][0]
        }
    }
        
    def retrieve_images(self):
        return getMultiAdapter((self.gallery, self)).getImageInformation()

class BasicImageInformationRetriever(BaseImageInformationRetriever):
    implements(IImageInformationRetriever)
    adapts(IObjectManager, IBasicAdapter)
    
    def getImageInformation(self):
        """
        A catalog search should be faster especially when there
        are a large number of images in the gallery. No need
        to wake up all the image objects.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        gallery_path = self.context.getPhysicalPath()
        images = catalog.searchResults(
            object_provides=IImageContent.__identifier__,
            path='/'.join(gallery_path)
        )

        # filter out image images that are not directly in its path..
        images = filter(lambda i: len(i.getPath().split('/')) == len(gallery_path) + 1, images) 
        return map(self.assemble_image_information, images)

class BasicTopicImageInformationRetriever(BaseImageInformationRetriever):
    implements(IImageInformationRetriever)
    adapts(IATTopic, IBasicAdapter)
    
    def getImageInformation(self):
        query = self.context.buildQuery()
        if query is not None:
            query.update({'object_provides' : IImageContent.__identifier__})
            catalog = getToolByName(self.context, 'portal_catalog')
            images = catalog(query)
            return map(self.assemble_image_information, images)
        else:
            return []
        
 
