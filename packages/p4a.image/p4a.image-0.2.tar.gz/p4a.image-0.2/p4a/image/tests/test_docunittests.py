import unittest
from zope.component import testing
from zope.testing import doctestunit

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocTestSuite('p4a.image.utils'),
        doctestunit.DocFileSuite('migration.txt',
                                 package="p4a.image",
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),
        doctestunit.DocFileSuite('extraction.txt',
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown)
        ))
