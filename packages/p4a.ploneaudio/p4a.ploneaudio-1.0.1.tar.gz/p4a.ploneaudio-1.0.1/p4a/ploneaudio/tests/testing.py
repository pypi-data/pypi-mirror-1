from p4a import ploneaudio
from p4a.ploneaudio import sitesetup
from Products.PloneTestCase import PloneTestCase
from zope.app.component import hooks

DEPENDENCIES = ['CMFonFive', 'Archetypes']
if ploneaudio.has_ataudio_support():
    DEPENDENCIES.append('ATAudio')

PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

if ploneaudio.has_fatsyndication_support():
    PRODUCT_DEPENDENCIES += ['basesyndication', 'fatsyndication']
if ploneaudio.has_blobfile_support():
    DEPENDENCIES += ['BlobFile']

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    PloneTestCase.installProduct(dependency)

PRODUCTS = list(DEPENDENCIES)

PloneTestCase.setupPloneSite(products=PRODUCTS)

from Products.Five import zcml
import p4a.common
import p4a.audio
import p4a.ploneaudio
import plone.app.form

class IntegrationTestCase(PloneTestCase.PloneTestCase):
    """Plone based integration test for p4a.ploneaudio."""

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        zcml.load_config('configure.zcml', plone.app.form)
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', p4a.audio)
        zcml.load_config('configure.zcml', p4a.ploneaudio)
        zcml.load_config('configure.zcml', p4a.fileimage)
        hooks.setHooks()

        sitesetup.setup_portal(self.portal)

def testclass_builder(**kwargs):
    class GeneratedIntegrationTestCase(IntegrationTestCase):
        """Generated integration TestCase for p4a.ploneaudio."""

    for key, value in kwargs.items():
        setattr(GeneratedIntegrationTestCase, key, value)

    return GeneratedIntegrationTestCase
