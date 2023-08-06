Introduction
============

PIP = Picture in Picture

pipbox = picture boxes in Plone

Products.pipbox provides JQuery Tools support in Plone.
This allows lightbox-style popups that may be loaded as images, AJAX html,
or iframes.

pipbox currently does two things:

  1) loads JQuery Tools and its supporting images by loading plone.app.jquerytools;
  
  2) provides a framework for connecting JQuery Tools bling to CSS selectors 
     without JavaScript.

pipbox has been tested with Plone 3.3, and is intended to work with Plone 4.

Site setup for pipbox is table-driven, with settings in the table allowing
you to specify DOM elements via jquery selectors. These are usually going to
be <a href... /> or <img src... /> elements. You specify how the URL should be 
loaded (as an image, ajax or iframe). You may also optionally supply a regular 
expression search/replace pair for the URL and additional arguments for the 
JS engine.

Options are specified with Javascript object notation and stored in a property sheet 
in portal_properties.


Overlay examples
----------------

Let's say, for example, that you want to make clicking on news-item photos
open a lightbox-style larger version of the image. To do this, you'll need to 
specify:

 * A jquery style selector for a Plone element, e.g., ".newsImageContainer a"

 * "image" for the load method ("ajax" and "iframe" are other alternatives)
 
 * A regular expression search/replace to transform the href or src URL.
   In this example, we're changing the URL to point to the preview-sized
   image. So, our search/replace pair is "/image_view_fullscreen"
   and "_preview". 
   
 * You could also specify additional overlay configuration parameters.

Site setup for pipbox is table-driven, with a lines field in 
portal_properties.pipbox_properties.selector_specs. In this table, each line is a JSON 
object specification, So, all of the above will need to be a line like::

    {type:'overlay',subtype:'image',selector:'.newsImageContainer a',urlmatch:'/image_view_fullscreen$',urlreplace:'_preview'}

Another quick example, one that provides full-image popups for images placed via kupu::

    {type:'overlay', subtype:'image', selector:'img.image-right,img.image-left,img.image-inline', urlmatch:'/image_.+$',urlreplace:''}

What's different? We're targeting <img ... /> tags, which don't have href attributes.
pipbox picks up the target URL from the src attribute, so that we can have a popup view
of image elements that aren't linked to that view. Note also that we're using a real
regular expression in the search/replace so that we can strip off image_preview, image_mini,
etc.

And, a configuration to put the site map in an iframe popup with expose settings, picking up
the target from an href::

    {type:'overlay',subtype:'iframe',selector:'#siteaction-sitemap a',config:{expose:{color:'#00f'}}}

Tabs examples
-------------

jQuery Tools unifies tabs, vertical accordions and horizontal accordions as 'tabs'. Tabs are 
tied to 'panes' -- the DOM elements displayed when tabs are chosen.

Identify tabs by supplying a 'tabcontainer' selector and a 'tabs' selector that chooses tab 
elements within the container. Supply a 'panes' selector to find the displayed panes.

So, if we want to turn a display list with a "pbtabs" class selector into a tab display, we 
could use the setup::

{type:'tabs',tabcontainer:'dl.pbtabs',tabs:'dt',panes:'dl.tabs > dd'}

To help with CSS, pipbox will tag both the tabcontainer and the panes with 'pbactive' class 
selectors to help you make sure that tabs degrade gracefully when JS isn't available.

There's currently no CSS support for tabs; we'll probably add something that will look like 
Plone tabs. Also, there will likely be subtypes to support AJAX loading of tab content.


Options
-------

The complete options list:

 * type: 'overlay', 'tabs' (other JQuery Tools effects coming)
 
 * config: JQuery Tools configuration options in a dictionary
 
For overlays, add the options:

 * subtype: 'image' | 'iframe' | 'ajax'

 * selector: the JQuery selector to find your elements
 
 * urlmatch: Regular expression for a portion of the target URL
 
 * urlreplace: Replacement expression for the matched expression
 
 * width: Width of the popup. Leave unset to determine through CSS.
   Overriden by image width for image overlays.
 
 For AJAX overlays, add the option:
 
    * formselector: Used to specify the JQuery selector for any
      forms inside the loaded content that you want to be handled
      inside the overlay by doing an AJAX load to replace the overlay
      content.
      
    * noform: the action to take if an ajax form is submitted and the returned 
      content has nothing matching the formselector. Available actions include
      'close' to simply close the overlay, 'reload' to reload the page, and
      'redirect' to redirect to another page. If you choose 'redirect', you
      must specify the URL in the redirect option.
      
    * closeselector: use this to specify a JQuery selector that will be used
      to find elements within the overlay that should close the overlay if
      clicked. The most obvious example is a form's cancel button.
      
    * redirect: if you specify 'redirect' for the noform action, use the
      redirect option to specify the full target URL.
 
For tabs, add the options:

  * tabcontainer: A JQuery selector identifying the container for the tabs
  
  * tabs: A JQuery selector to identify the tabcontainer children which should 
    be tabs.
  
  * panes: A JQuery selector for the panes to tie to the tabs. 


AJAX
----

Some of the pipbox options allow use of AJAX to get content. When you're 
loading content into an overlay or tab via AJAX, you're nearly always 
going to want only part of the loaded content. For example, if you're 
picking up a Plone page, you may only want the #content div's contents.

To do this, just add a CSS (or JQuery) selector to the target URL. 
JQuery's load method (which pipbox uses) will only pick up the content inside
the selection.

For example, let's say that you wish to display the standard Plone site map 
in an overlay. You could use::

    {type:'overlay',subtype:'ajax',selector:'#siteaction-sitemap a',urlmatch:'$',urlreplace:' #content > *'}

The urlmatch/urlreplace code adds a selector to the end of the URL when it 
calls JQuery's load to get the content, picking up only what's inside the 
#content div.

If you don't specify a selection from the loaded page's DOM, you'll get 
everything inside the body section of the page.

Some browsers cache AJAX loads, so a random argument is added to URLs.


AJAX Forms
----------

pipbox can automatically handle having forms that are within the overlay 
by making an AJAX post action, then replacing the overlay content with the 
results.

Specify forms for this handling with the "formselector" option. The content 
filter specified in the original overlay is reused.

For example, if you wished to handle the standard Plone contact form in an 
overlay, you could specify::

    {type:'overlay',subtype:'ajax',selector:'#siteaction-contact a',urlmatch:'$',urlreplace:' #content>*', formselector:'form'}

Another example: using popups for the delete confirmation and rename forms (from the action menu)::

    {type:'overlay',subtype:'ajax',selector:'a#delete,a#rename',urlmatch:'$',urlreplace:' #region-content','closeselector':'[name=form.button.Cancel]'}
    
There are a couple of differences here. First, there is no form selector 
specified; that's because we don't want to install an ajax submit handler 
when we may be renaming or deleting the displayed object. Second, we specify 
a close selector so that pushing the cancel button will close the overlay
without bothering to submit the form.


Global Configuration
====================

You may specify global configuration parameters for jQuery Tools in
portal_properties.pipbox_properties.tools_config. As with selector options,
this is specified in a list of JSON specifications. Each specification
should contain a 'tool' property specifying the tool being configured.

For example, to configure all overlays to load quickly and use a light
expose effect, specify::

    {tool:'overlay', speed:'fast', expose:{color:'#fff', opacity:0.5, loadSpeed:200}}
    
See the jQuery Tools documentation for available configuration options.


Integration Tests
=================

Setup the test framework::

    >>> from zope.component import getMultiAdapter
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = 'http://nohost/plone'

We should already be installed, so there should be a product in the Products space::

    >>> from Products import pipbox

And, quickinstaller should know about us::

    >>> portal.portal_quickinstaller.isProductInstalled('pipbox')
    True


Property Sheet Installation
---------------------------

We'll use a portal_properties property sheet to store site setup::

    >>> 'pipbox_properties' in portal.portal_properties.objectIds()
    True

It's selector_specs field should contain an automatic activation
specification. Here's what's pre-installed::

    >>> my_props = portal.portal_properties.pipbox_properties
    >>> my_props.selector_specs
     ("{type:'overlay',subtype:'image',selector:'.newsImageContainer a',urlmatch:'/image_view_fullscreen$',urlreplace:''}", "{type:'overlay',subtype:'ajax',selector:'#portal-personaltools li a',urlmatch:'$',urlreplace:' #region-content > *',formselector:'form#login_form','noform':'reload'}", "{type:'overlay',subtype:'ajax',selector:'a#delete,a#rename',urlmatch:'$',urlreplace:' #region-content','closeselector':'[name=form.button.Cancel]'}")
    

Stylesheet View
---------------

Popup windows require style support.
We should have our stylesheet available as a view::

    >>> view = getMultiAdapter((portal, app.REQUEST), name=u'pipbox.css')
    >>> mycss = view()
    >>> mycss.find('PIPBox Stylesheet') > 0
    True

For ease of interpolating plone style properties, 
it's a dtml document, and should be interpreted as such::

    >>> mycss.find('<dtml') == -1
    True

The stylesheet should be installed in the CSS registry::

    >>> 'pipbox.css' in portal.portal_css.getResourceIds()
    True


Javascript Resource and View
----------------------------

We should have two items in the JS registry::

    >>> jsreg = portal.portal_javascripts
    >>> ids = jsreg.getResourceIds()
    >>> '++resource++pipbox.js' in ids and 'pipboxinit.js' in ids
    True

Open the main JS code item as a resource::

    >>> browser.open(portal_url+'/++resource++pipbox.js')

And, make sure it's got our code in it::

    >>> print browser.contents
    /*****************
    <BLANKLINE>
       PIPbox tools for attaching JQuery Tools bling to CSS with option
       parameter strings.
    <BLANKLINE>
    *****************/
    ...

We have initialization code for our settings in a view::

    >>> view = getMultiAdapter((portal, app.REQUEST), name=u'pipboxinit.js')
    
This should contain the specifications from our propery sheet::

    >>> print view()
    <BLANKLINE>
    pb.doConfig({tool:'overlay', speed:'fast', expose:{color:'#fff', opacity:0.5, loadSpeed:200}});
    pb.doSetup({type:'overlay',subtype:'image',selector:'.newsImageContainer a',urlmatch:'/image_view_fullscreen$',urlreplace:''});
    pb.doSetup({type:'overlay',subtype:'ajax',selector:'#portal-personaltools li a',urlmatch:'$',urlreplace:' #region-content > *',formselector:'form#login_form','noform':'reload'});
    pb.doSetup({type:'overlay',subtype:'ajax',selector:'a#delete,a#rename',urlmatch:'$',urlreplace:' #region-content','closeselector':'[name=form.button.Cancel]'});

