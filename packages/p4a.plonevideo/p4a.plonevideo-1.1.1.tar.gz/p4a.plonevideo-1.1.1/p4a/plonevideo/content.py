from zope import interface
from p4a.video import interfaces
from OFS.SimpleItem import SimpleItem

class VideoSupport(SimpleItem):
    """
    """

    interface.implements(interfaces.IVideoSupport)

    @property
    def support_enabled(self):
        return True
