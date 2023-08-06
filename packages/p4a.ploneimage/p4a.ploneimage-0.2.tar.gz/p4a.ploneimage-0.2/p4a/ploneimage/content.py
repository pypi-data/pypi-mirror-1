from zope import interface
from p4a.image import interfaces
from OFS.SimpleItem import SimpleItem

class ImageSupport(SimpleItem):
    """
    """

    interface.implements(interfaces.IImageSupport)

    @property
    def support_enabled(self):
        return True
