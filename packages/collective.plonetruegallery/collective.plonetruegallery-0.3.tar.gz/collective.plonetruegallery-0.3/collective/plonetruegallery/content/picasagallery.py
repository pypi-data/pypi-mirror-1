from interfaces import IGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from collective.plonetruegallery.validators import isValidAlbumValidator


schema = Schema((
    StringField(
        name="picasaUsername",
        widget=StringField._properties['widget'](
            label="Email address of who this album belongs to"
        ),
        schemata="picasa"
    ),
    StringField(
        name="picasaPassword",
        widget=PasswordWidget(
            label="Password",
            description="Only required if your album is not public"
        ),
        schemata="picasa"
    ),
    BooleanField(
        name="isPicasaPrivate",
        widget=BooleanField._properties['widget'](
            label="Is this a private album?",
            description="Password is required if it is."
        ),
        default=False,
        schemata="picasa"
    ),
    StringField(
        name="picasaAlbum",
        widget=StringField._properties['widget'](
            label="Album",
            description="Name of your picasa web album.  To not use a picasa web album, just leave this blank."
        ),
        schemata="picasa",
        validators=('isValidAlbumValidator',)
    ),
),
)

PicasaGallerySchema = schema.copy()

class PicasaGallery(ATFolder):
    """A folder which can contain other items."""
    
    #hack for password field that loses password on validation...
    picasa_password = ""
    
    schema         =  PicasaGallerySchema