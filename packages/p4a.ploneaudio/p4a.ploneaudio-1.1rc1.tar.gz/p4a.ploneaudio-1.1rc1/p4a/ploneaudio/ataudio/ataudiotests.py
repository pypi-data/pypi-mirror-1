from unittest import TestSuite
from p4a.ploneaudio import testing
from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
from Products.PloneTestCase import layer

def test_suite():
    suite = TestSuite()
    suite.layer = layer.ZCMLLayer
    suite.addTest(ZopeDocFileSuite(
        'migration.txt',
        package='p4a.ploneaudio.ataudio',
        test_class=testing.IntegrationTestCase,
        )
    )

    return suite
