from zope import interface
from p4a.audio import interfaces
from OFS.SimpleItem import SimpleItem

class AudioSupport(SimpleItem):
    """Simple persistent class that implements IAudioSupport.

      >>> support = AudioSupport('foo')
      >>> support.support_enabled
      True

    """

    interface.implements(interfaces.IAudioSupport)

    @property
    def support_enabled(self):
        return True
