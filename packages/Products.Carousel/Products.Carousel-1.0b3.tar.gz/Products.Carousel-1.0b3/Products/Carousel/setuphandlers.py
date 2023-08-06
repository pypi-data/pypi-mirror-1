from zope.component import getUtility
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.layout.viewlets.interfaces import IContentViews
from Products.Carousel.utils import hasViewlet, registerViewlet

def configureViewlet(gscontext):
    """ Add the Carousel viewlet to the plone.contentviews viewlet manager
        as a *local* adapter, if it's not already registered for a manager.
    """
    if gscontext.readDataFile('carousel_various.txt') is None:
        # don't run this step for other profiles
        return
    
    if not hasViewlet():
        registerViewlet(IContentViews)
        
        # make sure it's first in the content views manager
        storage = getUtility(IViewletSettingsStorage)
        skins = getattr(storage, '_order')
        for skinname in skins:
            values = list(skins[skinname].get('plone.contentviews', []))
            values.insert(0, 'Products.Carousel.viewlet')
            storage.setOrder('plone.contentviews', skinname, tuple(values))
