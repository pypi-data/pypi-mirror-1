Introduction
============

This module has no test at the moment. Use it at your own risk.

"customization over configuration"

This is the difference between this and collective.plonetruegallery 

I'm using truegallery as often as possible and the 0.8 and one very good release.
But I have not succeed in customizing it. The  main reason is truegallery embed
display configuration inside data and component and I want to customize display.

So in collective.gallery you will find simple and basic features.

Goals
=====

* Have a simple to customize gallery product for plone.
* Use only flash or JQuery based gallery/slider scripts.
* don't embed display configuration inside data, only in template and css

Default views
=============

Folder, Large Plone Folder, Topic and Link has now these available views:

* s3slider
* dewslider

Link has also 'picasa_slideshow' (slideshow flash from google) view.

Roadmap
=======

* 0.2: tests and better img size handling
* 0.3: cache
* 0.4: flickr
* 0.5: tags
* 0.6 -> 0.8: more jquery galleries
* 0.9: portlet Link and porlet collection support
* 1.0: first stable release
