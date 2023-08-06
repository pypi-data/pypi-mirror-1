Introduction
============

Products.pipbox provides lightbox / greybox / thickbox support in Plone.

The goal is that this support will be available via methods that wrap the 
Javascript implementation (currently ThickBox) so that it can change if 
necessary.

My current idea is that we'll have a table that will contain rows like:

 * A jquery style selector for a Plone element, e.g., ".newsImageContainer a"
 
 * A regular expression search/replace to transform the href URL, e.g.,
   changing "test-news-item/image/image_view_fullscreen" to
   "test-news-item/image". In this example, we're changing the URL to
   point to the full image.
   
 * Parameters which could include loading method (ajax, iframe, ...),
   and window parameters.

Also, the default window styles will be picked up from Plone stylesheet
properties.