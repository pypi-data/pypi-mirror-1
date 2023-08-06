Introduction
-------
collective.plonetruegallery is a Plone product that gives you a Gallery content type.  
It allows you to add regular Plone Galleries, Picasa Web Albums or even Flickr sets.  
It allows the user to display the gallery in 3 different sizes, choose between two 
different javascript gallery display types and customize transitions, effects, and timing.

Features
-------
* Flickr and Picasa Support!
* Gallery Content Type
* Customize gallery size, transition(limited transitions right now), timed and other settings
* Can use nested galleries
* Slideshow 2(with transition types)
* Nested galleries
* Pre-fetches gallery images

Flickr and Picasa Web Album Support
-------
* these packages are no longer a dependency of this package
* to add support for these type of galleries you must install additional packages
* install flickrapi version 1.2 for flickr support
* install gdata version 1.2.3 or higher for Picasa Web Album Support
* these can just be added to your buildout or installed with easy_install

Fetching of Images Explained
-------
* When rendering a gallery, it checks if the images have been fetched within 
the last 1440 minutes(one day). If they have not, then it fetches them again.  
It also re-fetches the gallery on edits and when images are added/removed from 
a gallery. Since images are never really added/removed from a flickr or picasa 
type, it'll only be re-fetched every day unless you force it.
* You can also force a specific gallery to be re-fetched by appending ``refresh`` 
to the gallery url
* You can manually refresh all galleries on the site by typing in a url like 
``mysite.com/refresh_all_galleries``  This means you can also setup a cron-like 
job to refresh all the galleries whenever you want to just so it isn't done while 
a user is trying to render a page.

This product's inspired usage was for the University of Wisconsin Oshkosh.


Implementation Notes
-------
I know this has very little test coverage.  It is very difficult to test something
that is so javascript intense and the fact that it relies on images makes it difficult also....
Me not having sufficient time for this pet project also factors in.

Credits
-------
Translations

* French - Sylvain Boureliou
