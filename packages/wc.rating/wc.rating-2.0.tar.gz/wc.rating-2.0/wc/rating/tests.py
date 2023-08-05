import unittest
from doctest import DocFileSuite

import zope.component.testing
from zope.annotation.attribute import AttributeAnnotations
from wc.rating.rating import rating_adapter

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.provideAdapter(AttributeAnnotations)
    zope.component.provideAdapter(rating_adapter)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     package='wc.rating',
                     setUp=setUp,
                     tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
