import unittest

from zope.component.testing import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

def configurationSetUp(self):
    setUp()
    import zgeo.geographer
    import zgeo.wfs
    import zope.component
    import zope.annotation
    import zope.app.publisher.browser
    import Products.Five
    import Products.Archetypes
    import Products.CMFCore
    import Products.GenericSetup
    XMLConfig('meta.zcml', zope.component)()
    XMLConfig('meta.zcml', zope.app.publisher.browser)()
    XMLConfig('meta.zcml', Products.Five)()
    XMLConfig('meta.zcml', Products.GenericSetup)()
    XMLConfig('meta.zcml', Products.CMFCore)()
    XMLConfig('configure.zcml', zope.annotation)()
    XMLConfig('configure.zcml', Products.Five)()
    XMLConfig('configure.zcml', Products.GenericSetup)()
    XMLConfig('configure.zcml', Products.Archetypes)()
    XMLConfig('configure.zcml', zgeo.geographer)()
    XMLConfig('configure.zcml', zgeo.wfs)()
    ztc.installProduct('PluginIndexes')
    ptc.setupPloneSite(products=[])
        
def test_suite():
    return unittest.TestSuite((
        DocFileSuite('tests/unit.txt', package='zgeo.wfs',
                    setUp=configurationSetUp,
                    tearDown=tearDown,
                    optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        DocFileSuite('geocatalog/rtree.txt', package='zgeo.wfs',
                    setUp=configurationSetUp,
                    tearDown=tearDown,
                    optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
