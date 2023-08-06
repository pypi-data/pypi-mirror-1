from Products.Archetypes.atapi import *
from collective.plonetruegallery.validators.flickr import *

FlickrSchema = Schema((
    StringField(
        name="flickrUsername",
        widget=StringField._properties['widget'](
            label="The username/id of your flickr account"
        ),
        schemata="flickr",
        validators=(ValidateFlickrUsername(),)
    ),
    StringField(
        name="flickrSet",
        widget=StringField._properties['widget'](
            label="Set",
            description="Name/id of your flickr set."
        ),
        schemata="flickr",
        validators=(ValidateFlickrSet(),)
    ),
),
)