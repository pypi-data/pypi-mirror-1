import unittest, doctest
from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite

def setUp(test):
    setup.placefulSetUp()

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite(
        (DocFileSuite('README.txt', package='ice.template',
                      setUp=setUp, tearDown=tearDown,
                      optionflags=doctest.NORMALIZE_WHITESPACE
                      | doctest.ELLIPSIS,),))
