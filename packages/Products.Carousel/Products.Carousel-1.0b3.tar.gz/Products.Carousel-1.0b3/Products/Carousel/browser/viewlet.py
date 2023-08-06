from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class CarouselViewlet(ViewletBase):
    __name__ = 'Products.Carousel.viewlet'
    
    def index(self):
        """
        Look up Carousel view separately from the viewlet, so the template
        can be customized via portal_view_customizations (which only knows
        about global templates), but we can still use a local registration
        for the viewlet.
        """
        return self.context.restrictedTraverse('@@carousel')()
