import os
import Acquisition
from OFS import Image as ofsimage
try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces

from zope import component
from zope import interface
from zope.app.event import objectevent

from p4a.audio import audioanno
from p4a.audio import interfaces
from p4a.audio import utils

from p4a.common.descriptors import atfield

from p4a.fileimage import file as p4afile
from p4a.fileimage import utils as fileutils

from Products.ATContentTypes import interface as atctifaces  
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

from zope.component import queryAdapter

import logging
logger = logging.getLogger('p4a.ploneaudio.atct')

DEFAULT_CHARSET = 'utf-8'

class ATCTFolderAudioProvider(object):
    interface.implements(interfaces.IAudioProvider)
    component.adapts(atctifaces.IATFolder)
    
    def __init__(self, context):
        self.context = context

    @property
    def audio_items(self):
        files = []
        for x in self.context.getFolderContents(full_objects=True):
            adapted = component.queryAdapter(x, interfaces.IAudio)
            if adapted is not None:
                files.append(adapted)

        return files

class ATCTBTreeFolderAudioProvider(ATCTFolderAudioProvider):
    interface.implements(interfaces.IAudioProvider)
    component.adapts(atctifaces.IATBTreeFolder)

class ATCTTopicAudioProvider(object):
    interface.implements(interfaces.IAudioProvider)
    component.adapts(atctifaces.IATTopic)
    
    def __init__(self, context):
        self.context = context

    @property
    def audio_items(self):
        files = []
        for x in self.context.queryCatalog(full_objects=True):
            adapted = component.queryAdapter(x, interfaces.IAudio)
            if adapted is not None:
                files.append(adapted)

        return files

class I18NMixin(object):
    @property
    def _default_charset(self):
        """The charset determined by the active Plone site to be the
        default.
        """

        charset = getattr(self, '_cached_default_charset', None)
        if charset is not None:
            return charset
        try:
            props = cmfutils.getToolByName(self.context, 'portal_properties')
            self._cached_default_charset = \
                                         props.site_properties.default_charset
        except:
            self._cached_default_charset = DEFAULT_CHARSET
        return self._cached_default_charset

    def _u(self, v):
        """Return the unicode object representing the value passed in an
        as error-immune manner as possible.
        """

        return utils.unicodestr(v, self._default_charset)

@interface.implementer(interfaces.IAudio)
@component.adapter(atctifaces.IATFile)
def ATCTFileAudio(context):
    if not interfaces.IAudioEnhanced.providedBy(context):
        return None
    return _ATCTFileAudio(context)

class ImageMixin(object):
    """Supports image field setting and getting."""

    def _get_audio_image(self):
        v = self.audio_data.get('audio_image', None)
        if v == None or v.get_size() == 0:
            return None
        return v
    def _set_audio_image(self, v):
        if v == interfaces.IAudio['audio_image'].missing_value:
            return
        upload = v
        if isinstance(upload, ofsimage.Image):
            image = upload
        else:
            image = ofsimage.Image(id=upload.filename, 
                                   title=upload.filename, 
                                   file=upload)
        self.audio_data['audio_image'] = image
    audio_image = property(_get_audio_image, _set_audio_image)

class _ATCTFileAudio(ImageMixin, audioanno.AnnotationAudio, I18NMixin):
    """An IAudio adapter designed to handle ATCT based file content."""

    interface.implements(interfaces.IAudio)
    component.adapts(atctifaces.IATFile)

    ANNO_KEY = 'p4a.ploneaudio.atct.ATCTFileAudio'

    title = atfield('title', 'context')
    description = atfield('description', 'context')

    def _load_audio_metadata(self):
        """Retrieve audio metadata from the raw file data and update
        this object's appropriate metadata fields.
        """

        mime_type = self.context.get_content_type()
        accessor = component.queryAdapter(self.context, 
                                          interfaces.IAudioDataAccessor,
                                          unicode(mime_type))
        if accessor is not None:
            field = self.context.getPrimaryField()
            filename = fileutils.write_ofsfile_to_tempfile \
                       (field.getEditAccessor(self.context)())
            accessor.load(filename)
            os.remove(filename)

    def _save_audio_metadata(self):
        """Write the audio metadata fields of this object as metadata
        on the raw file data.
        """

        mime_type = self.context.get_content_type()
        accessor = component.queryAdapter(self.context, 
                                          interfaces.IAudioDataAccessor,
                                          unicode(mime_type))
        if accessor is not None:
            field = self.context.getPrimaryField()
            filename = fileutils.write_ofsfile_to_tempfile \
                       (field.getEditAccessor(self.context)())
            accessor.store(filename)

            zodb_file = field.getEditAccessor(self.context)()
            fin = open(filename, 'rb')
            # very inefficient, loading whole file in memory upon upload
            # TODO: fix in-memory loading
            data, size = zodb_file._read_data(fin)
            zodb_file.update_data(data, mime_type, size)
            fin.close()

            os.remove(filename)

    def _get_file(self):
        field = self.context.getPrimaryField()
        return field.getEditAccessor(self.context)()
    def _set_file(self, v):
        if v != interfaces.IAudio['file'].missing_value:
            field = self.context.getPrimaryField()
            field.getMutator(self.context)(v)
    file = property(_get_file, _set_file)

    @property
    def audio_type(self):
        mime_type = self.context.get_content_type()
        accessor = component.getAdapter(self.context, 
                                        interfaces.IAudioDataAccessor,
                                        unicode(mime_type))
        return accessor.audio_type

    def __str__(self):
        return '<p4a.audio ATCTFileAudio title=%s>' % self.title
    __repr__ = __str__

class _ATCTFolderishAudioContainer(ImageMixin,
                                   audioanno.AnnotationAudioContainer,
                                   I18NMixin):
    """An IAudioContainer adapter designed to handle ATCT based file content.
    """

    interface.implements(interfaces.IAudioContainer)
    component.adapts(atctifaces.IATFolder)

    ANNO_KEY = 'p4a.ploneaudio.atct.ATCTFolderAudioContainer'

    def __str__(self):
        return '<p4a.audio ATCTFolderishAudio title=%s>' % self.title
    __repr__ = __str__

@interface.implementer(interfaces.IAudioContainer)
@component.adapter(atctifaces.IATFolder)
def ATCTFolderAudioContainer(context):
    if not interfaces.IAudioContainerEnhanced.providedBy(context):
        return None
    return _ATCTFolderishAudioContainer(context)

@interface.implementer(interfaces.IAudioContainer)
@component.adapter(atctifaces.IATTopic)
def ATCTTopicAudioContainer(context):
    if not interfaces.IAudioContainerEnhanced.providedBy(context):
        return None
    return _ATCTFolderishAudioContainer(context)

@interface.implementer(interfaces.IAudioContainer)
@component.adapter(atctifaces.IATBTreeFolder)
def ATCTBTreeFolderAudioContainer(context):
    if not interfaces.IAudioContainerEnhanced.providedBy(context):
        return None
    return _ATCTFolderishAudioContainer(context)

def load_metadata(obj, evt):
    """An event handler for loading metadata.
    """

    obj._load_audio_metadata()

def sync_audio_metadata(obj, evt):
    """An event handler for saving id3 tag information back onto the file.
    Also updates annotations.
    """

    if interfaces.IAudio.providedBy(obj):
        audio = obj
        obj = obj.context
    else:
        audio = interfaces.IAudio(obj)

    annotations = annointerfaces.IAnnotations(obj)
    annodata = annotations.get(audio.ANNO_KEY, None)
    for description in evt.descriptions:
        if isinstance(description, objectevent.Attributes):
            attrs = description.attributes
            orig = {}
            for key in attrs:
                if key != 'file' and hasattr(audio, key):
                    orig[key] = getattr(audio, key)
                    if annodata is not None:
                        annodata[key] = orig[key]
            if 'file' in attrs:
                audio._load_audio_metadata()
                for key, value in orig.items():
                    setattr(audio, key, value)
    audio._save_audio_metadata()

def attempt_media_activation(obj, evt):
    """Try to activiate the media capabilities of the given object.
    """

    activator = interfaces.IMediaActivator(obj)

    if activator.media_activated:
        return

    mime_type = obj.get_content_type()
    try:
        accessor = component.getAdapter(obj,
                                        interfaces.IAudioDataAccessor,
                                        unicode(mime_type))
    except Exception, e:
        accessor = None

    if accessor is not None:
        activator.media_activated = True
        update_dublincore(obj, evt)
        update_catalog(obj, evt)

def update_dublincore(obj, evt):
    """Update the dublincore properties.
    """

    audio = interfaces.IAudio(obj)
    annotations = annointerfaces.IAnnotations(obj)
    data = annotations.get(audio.ANNO_KEY, None)
    obj.setTitle(data.get('title', u''))

def update_catalog(obj, evt):
    """Reindex the object in the catalog.
    """

    obj.reindexObject()

def feature_activated(evt):
    if evt.enhancedinterface is interfaces.IAudioContainerEnhanced:
        # we want to remove any dynamic view fti layout that was set so our
        # audio view is displayed properly
        obj = Acquisition.aq_base(evt.object)
        if hasattr(obj, 'layout'):
            del obj.layout
