collective.plonetruegallery Documentation
=========================================

Introduction
------------
collective.plonetruegallery is a Plone product that implements a very customizable and sophisticated gallery. It allows you to add regular Plone Galleries, Picasa Web Albums or even Flickr sets.  It also allows the user to display the gallery in 3 different sizes, choose between two different javascript gallery display types and customize transitions, effects, and timing. This project aims to be everything you need for a Gallery in Plone.

How It Works
------------
All you need to do is select the ``Gallery View`` from the ``Display`` drop down item for any Folder or Collection content type. Once that is done, a ``Gallery Settings`` tab is enabled for the type. With this, you can customize the various settings for the Gallery.


Features
--------
* Flickr and Picasa Support!
* Customize gallery size, transition(limited transitions right now), timed and other settings
* Can use nested galleries
* Slideshow 2(with transition types), Highslide JS and Fancybox display types
* Pre-fetches gallery images


Flickr and Picasa Web Album Support
-----------------------------------
* these packages are no longer a dependency of this package
* to add support for these type of galleries you must install additional packages
* install flickrapi version 1.2 for flickr support
* install gdata version 1.2.3 or higher for Picasa Web Album Support
* these can just be added to your buildout or installed with easy_install


Upgrading
---------
The upgrade to version 0.8* is an important and large update. Basically, it gets rid of the Gallery type, replaces it with the regular Folder type along with a new view applied to the folder, namely the "Gallery View." 

Also, when you install the new product, your galleries will *NOT* work until you've run the upgrade step.

One more thing, upgrading will also mean that the ``classic`` display type is no longer supported. Your gallery will be gracefully migrated, so no worries on that end. Also, the new gallery display types are much more appealing in many ways. It is just that you may not like the change in look of the gallery.

Right now, this is only tested and supported on Plone 3.3*


Installation
------------
Since this product depends on plone.app.z3cform, you'll need to add a few overrides for products versions in your buildout. Good news is that is you're using any other product that uses plone.app.z3cform, you'll already be good to go.

Basically, you'll need to add these to your buildout versions section::

    [versions]
    z3c.form = 1.9.0
    zope.i18n = 3.4.0
    zope.testing = 3.4.0
    zope.component = 3.4.0
    zope.securitypolicy = 3.4.0
    zope.app.zcmlfiles = 3.4.3


Fetching of Images Explained
----------------------------
* When rendering a picasa or flickr gallery, it checks if the images have been fetched within a day. If they have not, then it re-fetches the images for the gallery. 
* You can also force a specific gallery to be re-fetched by appending ``@@refresh`` to the gallery url
* You can manually refresh all galleries on the site by typing in a url like ``mysite.com/@@refresh_all_galleries``  This means you can also setup a cron-like job to refresh all the galleries whenever you want to, just so it isn't done while a user is trying to render a page.

This product's inspired usage was for the University of Wisconsin Oshkosh.


Credits
=======

Coding Contributions
--------------------
* Patrick Gerken - huge help with 0.8 release

Translations
------------
* French - Sylvain Boureliou
* Norwegian - Espen Moe-Nilssen
* Brazilian Portuguese - Diego Rubert
* Finnish - Ilja Everila
