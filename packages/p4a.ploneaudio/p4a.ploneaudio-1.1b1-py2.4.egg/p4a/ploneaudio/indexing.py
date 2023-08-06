from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from p4a.audio import interfaces
from p4a.audio.genre import GENRE_VOCABULARY
from zope.component import queryAdapter
from zope.component.interfaces import ComponentLookupError

def audio_artist(object, portal, **kwargs):
    """Return the name of the artist in the audio file for use in
    searching the catalog.
    """

    try:
        audiofile = interfaces.IAudio(object)
        return audiofile.artist
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('audio_artist', audio_artist)

def audio_genre_id(object, portal, **kwargs):
    """Return the genre id of the audio file for use in searching
    the catalog.
    """

    try:
        audiofile = interfaces.IAudio(object)
        return audiofile.genre
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('audio_genre_id', audio_genre_id)

def audio_track(object, portal, **kwargs):
    """Return the track number of the file for use in sorting in
    catalog queries.
    """

    try:
        audiofile = interfaces.IAudio(object)
        return audiofile.idtrack
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('audio_track', audio_track)

def SearchableText(obj, portal, **kwargs):
    """ Used by the catalog for basic full text indexing """

    charset = obj.getCharset()
    audiofile = interfaces.IAudio(obj, None)

    if audiofile is not None:
        if audiofile.genre in GENRE_VOCABULARY:
            genre = GENRE_VOCABULARY.getTerm(audiofile.genre).title
        else:
            genre = ''
        return_list = [obj.SearchableText(),
                       audiofile.artist.encode(charset),
                       genre.encode(charset)]
        return ' '.join([x.strip() for x in return_list if x])
    else:
        return obj.SearchableText()

registerIndexableAttribute('SearchableText', SearchableText)

