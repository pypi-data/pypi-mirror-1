import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from zope.testing import doctest
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig
import zope.app.component
import zgeo.kml

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def configurationSetUp(test):
    setUp()
    try:
        import Products.Five.browser
        XMLConfig('meta.zcml', Products.Five.browser)()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('configure.zcml', zgeo.kml)()
    except:
        pass

def configurationTearDown(test):
    tearDown()


def test_suite():
    return unittest.TestSuite([
        doctestunit.DocFileSuite(
            'README.txt',
            package='zgeo.kml',
            setUp=testing.setUp,
            tearDown=testing.tearDown
            ),
        doctestunit.DocFileSuite(
            'integration.txt',
            package='zgeo.kml',
            setUp=configurationSetUp,
            tearDown=configurationTearDown,
            optionflags=optionflags,
            ),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
