import p4a.ploneaudio.indexing
import p4a.ploneaudio.sitesetup

def has_package(pkgstr):
    """Check to see if a package can be imported.

      >>> has_package('sys')
      True
      >>> has_package('foo')
      False
    """

    try:
        __import__(pkgstr, globals(), locals(), pkgstr)
    except ImportError, e:
        return False
    return True

def has_fatsyndication_support():
    """Return whether fatsyndication is available.

      >>> has_fatsyndication_support() in (True, False)
      True
    """

    return has_package('Products.fatsyndication')

def has_ataudio_support():
    """Return whether ataudio is available.

      >>> has_ataudio_support() in (True, False)
      True
    """

    return has_package('Products.ATAudio')

def has_blobfile_support():
    """Return whether blobfile is available.

      >>> has_blobfile_support() in (True, False)
      True
    """

    return has_package('Products.BlobFile')
