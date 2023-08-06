from Products.Carousel.utils import unregisterViewlet

def uninstall(portal, reinstall=False):
    if not reinstall:
        unregisterViewlet()
