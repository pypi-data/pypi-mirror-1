from zope import interface
from zope import component
from p4a import subtyper
from p4a.audio import interfaces
from Products.ATContentTypes import interface as atctifaces

class FolderMediaActivator(object):
    """An adapter for seeing the activation status or toggling activation.
    """

    interface.implements(interfaces.IMediaActivator)
    component.adapts(atctifaces.IATFolder)

    def __init__(self, context):
        self.context = context

    media_activated = subtyper.activated('p4a.audio.FolderAudioContainer',
                                         'context')

class BTreeFolderMediaActivator(object):
    """An adapter for seeing the activation status or toggling activation.
    """

    interface.implements(interfaces.IMediaActivator)
    component.adapts(atctifaces.IATBTreeFolder)

    def __init__(self, context):
        self.context = context

    media_activated = subtyper.activated('p4a.audio.FolderAudioContainer',
                                         'context')

class TopicMediaActivator(object):
    """An adapter for seeing the activation status or toggling activation.
    """

    interface.implements(interfaces.IMediaActivator)
    component.adapts(atctifaces.IATTopic)

    def __init__(self, context):
        self.context = context

    media_activated = subtyper.activated('p4a.audio.TopicAudioContainer',
                                         'context')
