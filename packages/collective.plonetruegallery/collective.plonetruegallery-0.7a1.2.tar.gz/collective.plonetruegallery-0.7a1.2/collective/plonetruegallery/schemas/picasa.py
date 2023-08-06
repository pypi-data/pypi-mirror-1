from Products.Archetypes.atapi import *
from collective.plonetruegallery.validators.picasa import *
from collective.plonetruegallery.utils import PTGMessageFactory as _

PicasaSchema = Schema((
    StringField(
        name="picasaUsername",
        widget=StringField._properties['widget'](
            label=_(u"label_picasa_username", 
                default=u"Email address of who this album belongs to(including @gmail.com)")
        ),
        schemata="picasa",
        validators=(ValidatePicasaUsername(),)
    ),
    #can't figure out how to not make the user enter in their password on every edit
    #postback = True and populate = True doesn't work
    StringField(
        name="picasaPassword",
        widget=PasswordWidget(
            label=_(u"label_picasa_password", default=u"Password"),
            description=_(u"description_picasa_password", 
                default=u"Only required if your album is not public.  It is recommended to just make your album public."),
        ),
        schemata="picasa",
        validators=(ValidatePicasaPassword(),)
    ),
    BooleanField(
        name="isPicasaPrivate",
        widget=BooleanField._properties['widget'](
            label=_(u"label_picasa_private", default=u"Is this a private album?"),
            description=_(u"description_picasa_private", default=u"Password is required if it is.")
        ),
        default=False,
        schemata="picasa",
        validators=(ValidateIsPicasaPrivate(),)
    ),
    StringField(
        name="picasaAlbum",
        widget=StringField._properties['widget'](
            label=_(u"label_picasa_album", default=u"Album"),
            description=_(u"description_picasa_album", 
                default=u"""Name of your picasa web album.  """
                        u"""This will be the qualified name you'll see in the address bar.  """
                        u"""If you have an album named "My Favorites" in the address bar you'll """
                        u"""most likely see that album name is "MyFavorites"  Use that name... """)
        ),
        schemata="picasa",
        validators=(ValidatePicasaAlbum(),)
    ),
),
)
