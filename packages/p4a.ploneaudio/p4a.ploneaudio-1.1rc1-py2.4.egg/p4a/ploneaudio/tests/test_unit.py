import doctest
import unittest
from zope.testing import doctestunit
from zope.component import testing

def test_suite():
    suite = unittest.TestSuite()
    if __name__ not in ('__main__', 'p4a.ploneaudio.tests.test_unit'):
        return suite

    suite.addTest(doctestunit.DocTestSuite('p4a.ploneaudio'))
    suite.addTest(doctestunit.DocTestSuite('p4a.ploneaudio.content'))
    suite.addTest(doctestunit.DocFileSuite('atct.txt',
                                           package='p4a.ploneaudio',
                                           optionflags=doctest.ELLIPSIS,
                                           setUp=testing.setUp,
                                           tearDown=testing.tearDown))
    suite.addTest(doctestunit.DocFileSuite('indexing.txt',
                                           package='p4a.ploneaudio',
                                           optionflags=doctest.ELLIPSIS))
    suite.addTest(doctestunit.DocFileSuite('sitesetup.txt',
                                           package='p4a.ploneaudio',
                                           optionflags=doctest.ELLIPSIS))
    suite.addTest(doctestunit.DocFileSuite('syndication.txt',
                                           package='p4a.ploneaudio',
                                           optionflags=doctest.ELLIPSIS))

    return suite
