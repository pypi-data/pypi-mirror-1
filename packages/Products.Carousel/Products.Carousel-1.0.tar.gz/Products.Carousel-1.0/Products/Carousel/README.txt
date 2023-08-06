Introduction
============

Carousel is a tool for featuring a rotating set of banner images in any section
of your Plone site.  Features:

 * Different sets of banners can be used in different sections of the site.
 
 * Banners can link to another page in the site, or an external URL.
 
 * Banners rotate via a simple fade effect every 8 seconds.  This is
   implemented using the jQuery javascript library which is included with
   Plone, so it's pretty lightweight.
   
 * Clicking on the title of a banner jumps to it immediately.
 
 * Images will not rotate while the mouse cursor is hovering over the Carousel.


Compatibility
=============

Carousel requires Plone 3.0 or greater, mainly because it renders itself in a
viewlet.


Installation
============

Add Products.Carousel to your buildout's list of eggs, and re-run buildout.

Start up Zope and go to Site Setup, Add-on Products in your Plone site, and
install the Carousel product.


Using Carousel
==============

`A detailed guide to using Carousel <http://plone.org/products/carousel/documentation>`
is available.


Detailed overview and tests
===========================


Configuring a Carousel banner folder
------------------------------------

The items displayed by Carousel are known as "Carousel Banners" and can exist
within a "Carousel Folder" in any section of the site.  For purposes of
demonstration, let's add a Carousel folder to the root of the site.

Carousel folders are a matter of configuration more than content, so they don't
appear on the Add menu. Instead, there is a 'Configure banners' tab.  Clicking
it while within a section that doesn't yet have a Carousel folder will result
in the creation of a new one::

  >>> browser.open('http://nohost/plone')
  >>> browser.getLink('Configure banners').click()
  >>> browser.url
  'http://nohost/plone/carousel'

The new folder should now provide the ICarouselFolder interface::

  >>> from Products.Carousel.interfaces import ICarouselFolder
  >>> ICarouselFolder.providedBy(self.portal.carousel)
  True

If, on the other hand, we're in a folder that already has a Carousel folder,
the existing one will be used::

  >>> browser.goBack()
  >>> browser.getLink('Configure banners').click()
  >>> browser.url
  'http://nohost/plone/carousel'

And if we try to configure banners while we're already doing so, nothing
should change::

  >>> browser.getLink('Configure banners').click()
  >>> browser.url
  'http://nohost/plone/carousel'


Adding a Carousel banner
------------------------

Now that we're within the Carousel folder, we can add a Carousel banner using
the add menu::

  >>> browser.getLink('Carousel Banner').click()
  >>> browser.url
  'http://nohost/plone/carousel/portal_factory/Carousel Banner/carousel_banner.../edit'

We can set various things including a title, target URL, and image::

  >>> browser.getControl('Title').value = 'Pirates and Cowboys agree: Ninjas suck'
  >>> browser.getControl('URL').value = 'http://www.plone.org'
  >>> browser.getControl(name='image_file')
  <Control name='image_file' type='file'>
  >>> browser.getControl('Save').click()
  >>> 'Changes saved.' in browser.contents
  True
  

Viewing the banners
-------------------

Now if we return to the home page, where we initially configured the banners,
the banner we just added should be rendered (*before* the tabs)::

  >>> browser.open('http://nohost/plone')
  >>> browser.contents
  <BLANKLINE>
  ...Pirates and Cowboys...
  ...class="contentViews"...


Adding banners in other scenarios
---------------------------------

Non-structural folder - put the carousel in the containing folder

  >>> self.setRoles(['Manager'])
  >>> self.portal.invokeFactory('Folder', 'nonstructural')
  'nonstructural'
  >>> from zope.interface import alsoProvides
  >>> from Products.CMFPlone.interfaces import INonStructuralFolder
  >>> alsoProvides(self.portal.nonstructural, INonStructuralFolder)
  >>> browser.open('http://nohost/plone/nonstructural')
  >>> browser.getLink('Configure banners').click()
  >>> browser.url
  'http://nohost/plone/carousel'

Collection, not default item - put the carousel in the collection itself

  >>> self.portal.invokeFactory('Topic', 'topic')
  'topic'
  >>> browser.open('http://nohost/plone/topic')
  >>> browser.getLink('Configure banners').click()
  >>> browser.url
  'http://nohost/plone/topic/carousel'

Collection, as default item -- put the carousel in the containing folder

  >>> self.portal.default_page = 'topic'
  >>> browser.open('http://nohost/plone/topic')
  >>> browser.getLink('Configure banners').click()
  >>> browser.url
  'http://nohost/plone/carousel'
