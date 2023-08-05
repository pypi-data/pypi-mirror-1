from zope import component
from zope import interface
from zope.schema import vocabulary 
from p4a.audio import interfaces
from Products.CMFCore import utils as cmfutils
from Products.fatsyndication import adapters as fatadapters
from Products.basesyndication import interfaces as baseinterfaces

from p4a.audio import genre

class AudioContainerFeed(fatadapters.BaseFeed):
    interface.implements(baseinterfaces.IFeed)
    component.adapts(interfaces.IAudioContainerEnhanced)

class AudioContainerFeedSource(fatadapters.BaseFeedSource):
    interface.implements(baseinterfaces.IFeedSource)
    component.adapts(interfaces.IAudioContainerEnhanced)

    def getFeedEntries(self):
        """See IFeedSoure
        """
        audio_items = interfaces.IAudioProvider(self.context).audio_items
        return [baseinterfaces.IFeedEntry(x.context) 
                for x in audio_items]

class AudioFeed(fatadapters.BaseFeed):
    interface.implements(baseinterfaces.IFeed)
    component.adapts(interfaces.IAudioEnhanced)

class AudioFeedSource(fatadapters.BaseFeedSource):
    interface.implements(baseinterfaces.IFeedSource)
    component.adapts(interfaces.IAudioEnhanced)

    def getFeedEntries(self):
        """See IFeedSoure
        """
        return [baseinterfaces.IFeedEntry(self.context)]

class AudioFeedEntry(fatadapters.BaseFeedEntry):
    interface.implements(baseinterfaces.IFeedEntry)
    component.adapts(interfaces.IAudioEnhanced)
    
    def __init__(self, *args, **kwargs):
        fatadapters.BaseFeedEntry.__init__(self, *args, **kwargs)
        
        self.audio = interfaces.IAudio(self.context)
    
    def getBody(self):
        """See IFeedEntry.
        """
        return ''
    
    def getEnclosure(self):
        return baseinterfaces.IEnclosure(self.context)
    
    def getTitle(self):
        return self.audio.title
    
    def getArtist(self):
        """
        """
        return self.audio.artist
    
    def getDescription(self):
        """
        """
        return self.audio.description
    
    def getCategory(self):
        """
        """
        g = self.audio.genre
        if g in genre.GENRE_VOCABULARY:
            return genre.GENRE_VOCABULARY.getTerm(g).title
        return u''
    
    
class ATFileEnclosure(object):
    interface.implements(baseinterfaces.IEnclosure)
    component.adapts(interfaces.IAudioEnhanced)
    
    def __init__(self, context):
        self.context = context
    
    def getURL(self):
        return self.context.absolute_url()

    def getLength(self):
       return self.context.getFile().get_size()

    def __len__(self):
        return self.getLength()

    def getMajorType(self):
        return self.context.getFile().getContentType().split('/')[0]

    def getMinorType(self):
        return self.context.getFile().getContentType().split('/')[1]

    def getType(self):
        return self.context.getFile().getContentType()
