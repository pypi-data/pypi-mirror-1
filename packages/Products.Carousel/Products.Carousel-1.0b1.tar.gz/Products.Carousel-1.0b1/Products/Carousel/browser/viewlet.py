from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class CarouselViewlet(ViewletBase):
    __name__ = 'Products.Carousel.viewlet'
    index = ZopeTwoPageTemplateFile('viewlet.pt')
