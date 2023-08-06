from Products.Archetypes.atapi import *
from collective.plonetruegallery.validators.picasa import *

PicasaSchema = Schema((
    StringField(
        name="picasaUsername",
        widget=StringField._properties['widget'](
            label="Email address of who this album belongs to(including @gmail.com)"
        ),
        schemata="picasa",
        validators=(ValidatePicasaUsername(),)
    ),
    #can't figure out how to not make the user enter in their password on every edit
    #postback = True and populate = True doesn't work
    StringField(
        name="picasaPassword",
        widget=PasswordWidget(
            label="Password",
            description="Only required if your album is not public.  It is recommended to just make your album public.",
        ),
        schemata="picasa",
        validators=(ValidatePicasaPassword(),)
    ),
    BooleanField(
        name="isPicasaPrivate",
        widget=BooleanField._properties['widget'](
            label="Is this a private album?",
            description="Password is required if it is."
        ),
        default=False,
        schemata="picasa",
        validators=(ValidateIsPicasaPrivate(),)
    ),
    StringField(
        name="picasaAlbum",
        widget=StringField._properties['widget'](
            label="Album",
            description="""Name of your picasa web album.  This will be the qualified name you'll see in the address bar.  If you have an album named "My Favorites" in the address bar you'll most likely see that album name is "MyFavorites"  Use that name... """
        ),
        schemata="picasa",
        validators=(ValidatePicasaAlbum(),)
    ),
),
)
