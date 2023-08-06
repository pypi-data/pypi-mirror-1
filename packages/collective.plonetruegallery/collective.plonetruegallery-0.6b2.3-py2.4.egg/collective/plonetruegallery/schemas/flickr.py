from Products.Archetypes.atapi import *
from collective.plonetruegallery.validators.flickr import *
from collective.plonetruegallery.utils import PTGMessageFactory as _

FlickrSchema = Schema((
    StringField(
        name="flickrUsername",
        widget=StringField._properties['widget'](
            label=_(u"label_flickr_username", default=u"The username/id of your flickr account")
        ),
        schemata="flickr",
        validators=(ValidateFlickrUsername(),)
    ),
    StringField(
        name="flickrSet",
        widget=StringField._properties['widget'](
            label=_(u"label_flickr_set", default="Set"),
            description=_(u"description_flickr_set", default=u"Name/id of your flickr set.")
        ),
        schemata="flickr",
        validators=(ValidateFlickrSet(),)
    ),
),
)