from zope.interface import Interface

from Products.Carousel import CarouselMessageFactory as _

class ICarouselFolder(Interface):
    """Marker for a folder that can hold Carousel banners."""
    
class ICarouselBanner(Interface):
    """A carousel banner which may include an image, text, and/or link."""
    
    def getSize(scale=None):
        """ Wraps the getSize method of the image field.
        """
    
    def tag(**kw):
        """ Wraps the tag method of the image field."""

class ICarouselBrowserLayer(Interface):
    """Marker applied to the request during traversal of sites that
       have Carousel installed
    """
