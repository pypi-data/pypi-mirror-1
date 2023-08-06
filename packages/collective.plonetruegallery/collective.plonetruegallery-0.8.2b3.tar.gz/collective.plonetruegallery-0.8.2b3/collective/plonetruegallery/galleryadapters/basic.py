from collective.plonetruegallery.interfaces import IBasicAdapter, \
    IBasicGallerySettings, IImageInformationRetriever, IGalleryAdapter
from Products.ATContentTypes.content.image import ATImageSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getMultiAdapter, adapts, getUtility
from base import BaseAdapter, BaseImageInformationRetriever
from collective.plonetruegallery import PTGMessageFactory as _
from Products.ATContentTypes.interface.image import IImageContent
from OFS.interfaces import IObjectManager
from Products.ATContentTypes.interface import IATTopic
from Products.Archetypes.interfaces import IBaseFolder
from Products.CMFCore.interfaces import IPropertiesTool
from plone.memoize.view import memoize_contextless

class BasicAdapter(BaseAdapter):
    implements(IBasicAdapter, IGalleryAdapter)

    name = u"basic"
    description = _(u"label_default_gallery_type",
        default=u"Use Plone To Manage Images")

    schema = IBasicGallerySettings
    cook_delay = 0

    size_map = {
		'small' : 'mini',
		'medium' : 'preview',
		'large' : 'large',
		'thumb' : 'tile' 
	}
    _inverted_size_map = dict([(v, k) for (k, v) in size_map.iteritems()])

    _sizes = {
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
        'thumb': {
            'width' : ATImageSchema['image'].sizes['tile'][0],
            'height' : ATImageSchema['image'].sizes['tile'][1]
        }
    }
    
    # since some default sizes Plone has are rather small,
    # let's setup a mechanism to upgrade sizes.
    minimum_sizes = {
        'small' : {
            'width' : 320,
            'height' : 320,
            'next_scale' : 'preview'
        },
        'medium' : {
            'width' : 576,
            'height' : 576,
            'next_scale' : 'large'
        }
    }
    
    
    
    @property
    @memoize_contextless
    def sizes(self):
        props = getUtility(IPropertiesTool)
        imaging_properties = props.get('imaging_properties', None)

        if imaging_properties:
            # user has plone.app.imaging installed, use
            # these image size settings
            _allowed_sizes = imaging_properties.getProperty('allowed_sizes')
            allowed_sizes = {}

            for size in _allowed_sizes:
                scale_name, size = size.split(' ')
                width, height = size.split(':')
                width = int(width)
                height = int(height)
                if scale_name not in self._inverted_size_map:
                    continue
                size_name = self._inverted_size_map[scale_name]
                allowed_sizes[size_name] = {'width' : width, 'height' : height}
            
                if size_name in self.minimum_sizes:
                    if width < self.minimum_sizes[size_name]['width']:
                        allowed_sizes[size_name]['width'] = self.minimum_sizes[size_name]['width']
                    elif height < self.minimum_sizes[size_name]['height']:
                        allowed_sizes[size_name]['height'] = self.minimum_sizes[size_name]['height']

                    self.size_map[size_name] = self.minimum_sizes[size_name]['next_scale']
                
            return allowed_sizes
        else:
            return self._sizes

    def retrieve_images(self):
        return getMultiAdapter((self.gallery, self)).getImageInformation()

class BasicImageInformationRetriever(BaseImageInformationRetriever):
    implements(IImageInformationRetriever)
    adapts(IBaseFolder, IBasicAdapter)

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
            path='/'.join(gallery_path),
            sort_on = 'getObjPositionInParent'
        )

        # filter out image images that are not directly in its path..
        images = filter(lambda i: len(i.getPath().split('/')) == len(gallery_path) + 1, images)
        return map(self.assemble_image_information, images)

    def get_link_url(self, image):
        retval = super(BasicImageInformationRetriever, self).\
            get_link_url(image)
        if self.pm.isAnonymousUser():
            return retval
        return retval + "/view"

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

    def get_link_url(self, image):
        retval = super(BasicTopicImageInformationRetriever, self).\
            get_link_url(image)
        if self.pm.isAnonymousUser():
            return retval
        return retval + "/view"
