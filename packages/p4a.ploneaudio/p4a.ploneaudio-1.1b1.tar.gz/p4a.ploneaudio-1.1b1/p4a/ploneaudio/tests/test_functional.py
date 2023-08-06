import os
import doctest
import unittest
from App import Common

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from p4a import ploneaudio

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, PloneSite

@onsetup
def load_package_products():
    import p4a.z2utils
    import p4a.common
    import p4a.fileimage
    import p4a.subtyper
    import p4a.audio
    import p4a.ploneaudio

    fiveconfigure.debug_mode = True
    zcml.load_config('meta.zcml', p4a.subtyper)
    zcml.load_config('configure.zcml', p4a.subtyper)
    zcml.load_config('configure.zcml', p4a.common)
    zcml.load_config('configure.zcml', p4a.fileimage)
    zcml.load_config('configure.zcml', p4a.audio)
    zcml.load_config('configure.zcml', p4a.ploneaudio)
    fiveconfigure.debug_mode = False
    ztc.installPackage('p4a.ploneaudio')

load_package_products()
ptc.setupPloneSite(products=['p4a.ploneaudio'])

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(ztc.FunctionalDocFileSuite('plone-audio.txt',
                                             package='p4a.ploneaudio',
                                             optionflags=doctest.ELLIPSIS,
                                             test_class=ptc.FunctionalTestCase))

    suite.addTest(ztc.FunctionalDocFileSuite('syndication-integration.txt',
                                             package='p4a.ploneaudio',
                                             optionflags=doctest.ELLIPSIS,
                                             test_class=ptc.FunctionalTestCase))

    suite.addTest(ztc.FunctionalDocFileSuite('browser.txt',
                                             package='p4a.ploneaudio',
                                             optionflags=doctest.ELLIPSIS,
                                             test_class=ptc.FunctionalTestCase))

    import p4a.audio.tests
    pkg_home = Common.package_home({'__name__': 'p4a.audio.tests'})
    samplesdir = os.path.join(pkg_home, 'samples')

    fields = dict(
        title=u'Test of the Emercy Broadcast System',
        artist=u'Rocky Burt',
        album=u'Emergencies All Around Us',
        )
    SAMPLES = (
        (os.path.join(samplesdir, 'test-full.mp3'), 'audio/mpeg', fields),
        (os.path.join(samplesdir, 'test-full.ogg'), 'application/ogg', fields),
        (os.path.join(samplesdir, 'test-no-images.mp3'), 'audio/mpeg', fields),
    )

    for relsamplefile, mimetype, samplefields in SAMPLES:
        class MediaTestCase(ptc.FunctionalTestCase):
            required_mimetype = mimetype
            samplefile = os.path.join(samplesdir, relsamplefile)
            file_content_type = 'File'
            fields = samplefields

        test = ztc.FunctionalDocFileSuite('plone-audio-impl.txt',
                                          package='p4a.ploneaudio',
                                          optionflags=doctest.ELLIPSIS,
                                          test_class=MediaTestCase)

        suite.addTest(test)

    return suite
