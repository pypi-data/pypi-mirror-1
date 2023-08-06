from p4a.audio import interfaces
from p4a.ploneaudio import content
from p4a.common import site
from p4a.z2utils import indexing
from p4a.z2utils import utils

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName, SimpleRecord 

from p4a.audio.interfaces import IAudio

import logging
logger = logging.getLogger('p4a.ploneaudio.sitesetup')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False

def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)
    setup_indexes(portal)
    setup_metadata(portal)
    setup_smart_folder_indexes(portal)

    qi = getToolByName(portal, 'portal_quickinstaller')
    qi.installProducts(['CMFonFive'])

def setup_site(site):
    """Install all necessary components and configuration into the
    given site.

    """

    sm = site.getSiteManager()
    if not sm.queryUtility(interfaces.IAudioSupport):
        # registerUtility api changed between Zope 2.9 and 2.10
        if HAS_FLSM:
            sm.registerUtility(content.AudioSupport('audio_support'),
                               interfaces.IAudioSupport)
        else:
            sm.registerUtility(interfaces.IAudioSupport,
                               content.AudioSupport('audio_support'))

def setup_indexes(portal):
    """Install specific indexes for the audio metadata fields
    so they are searchable.

    """

    out = StringIO()
    pc = getToolByName(portal, 'portal_catalog')

    indexing.ensure_object_provides(portal)

    if not 'audio_genre_id' in pc.indexes():
        pc.addIndex('audio_genre_id', 'FieldIndex')
        pc.manage_reindexIndex('audio_genre_id')
        print >>out, 'The FieldIndex "audio_genre_id" was successfully created'

    if not 'audio_artist' in pc.indexes():
        extra = SimpleRecord(lexicon_id='plaintext_lexicon',
                             index_type='Okapi BM25 Rank')

        pc.addIndex('audio_artist', 'ZCTextIndex', extra)
        pc.manage_reindexIndex('audio_artist')
        print >>out, 'The ZCTextIndex "audio_artist" was successfully created'

    if not 'audio_track' in pc.indexes():
        pc.addIndex('audio_track', 'FieldIndex')
        pc.manage_reindexIndex('audio_track')
        print >>out, 'The FieldIndex "audio_track" was successfully created'

    if not 'Format' in pc.indexes():
        pc.addIndex('Format', 'FieldIndex')
        pc.manage_reindexIndex('Format')
        print >>out, 'The FieldIndex "Format" was successfully created'

def setup_metadata(portal):
    """Adds the specified columns to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""

    out = StringIO()
    pc = getToolByName(portal, 'portal_catalog', None)

    try:
        pc.delColumn('audio_artist')
    except:
        pass

    reindex = []

    pc.manage_addColumn('audio_artist')
    reindex.append('audio_artist')

    if reindex:
        pc.refreshCatalog()

    print >>out, 'The metadata "audio_artist" was successfully added.'


INDEX_MAPPING = {'audio_artist':
                    {'name': 'Artist name',
                     'description': 'The name of the artist.',
                     'enabled': True,
                     'criteria': ('ATSimpleStringCriterion',)},
                 'audio_genre_id':
                    {'name': 'Genre',
                     'description': 'The genre id of the song.'
                                    'this is a number 0-147. '
                                    'See genre.py for the genre names.',
                     'enabled': True,
                     'criteria': ('ATSimpleIntCriterion',)},
                 'Format':
                    {'name': 'MIME Types',
                     'description': 'The MIME type of the file. '
                                 'For an MP3 file, this is audio/mpeg.',
                     'enabled': True,
                     'criteria': ('ATSimpleStringCriterion',)},
                 }

def setup_smart_folder_indexes(portal):
    """Adds the default indexes to be available from smartfolders"""
    atct_config = getToolByName(portal, 'portal_atct')

    for index, index_info in INDEX_MAPPING.items():
        atct_config.updateIndex(index, friendlyName=index_info['name'],
                                description=index_info['description'],
                                enabled=index_info['enabled'],
                                criteria=index_info['criteria'])
        atct_config.updateMetadata(index, friendlyName=index_info['name'],
                                   description=index_info['description'],
                                   enabled=True)

def _cleanup_utilities(site):
    raise NotImplementedError('Current ISiteManager support does not '
                              'include ability to clean up')

def unsetup_portal(portal):
    count = utils.remove_marker_ifaces(portal, \
        [interfaces.IAudioEnhanced, interfaces.IAudioContainerEnhanced])
    logger.warn('Removed IAudioEnhanced and IAudioContainerEnhanced '
                'interfaces from %i objects for cleanup' % count)
