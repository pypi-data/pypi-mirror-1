from zope.interface import alsoProvides
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Carousel.interfaces import ICarouselFolder
from Products.Carousel.utils import addPermissionsForRole

CAROUSEL_ID = 'carousel'

class CarouselFolderManager(BrowserView):
    
    def __call__(self):
        
        if ICarouselFolder.providedBy(self.context):
            carousel = self.context
        elif hasattr(self.context.aq_base, CAROUSEL_ID):
            carousel = getattr(self.context, CAROUSEL_ID)
        else:
            pt = getToolByName(self.context, 'portal_types')
            newid = pt.constructContent('Folder', self.context, 'carousel', title='Carousel Banners', excludeFromNav=True)
            carousel = getattr(self.context, newid)
            
            # mark the new folder as a Carousel folder
            alsoProvides(carousel, ICarouselFolder)
            
            # make sure Carousel banners are addable within the new folder
            addPermissionsForRole(carousel, 'Manager', ('Carousel: Add Carousel Banner',))
            
            # make sure *only* Carousel banners are addable
            carousel.setConstrainTypesMode(1)
            carousel.setLocallyAllowedTypes(['Carousel Banner'])
            carousel.setImmediatelyAddableTypes(['Carousel Banner'])

        self.request.RESPONSE.redirect(carousel.absolute_url())
