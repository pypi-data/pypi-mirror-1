import unittest
from zope.app.testing import functional

functional.defineLayer('TestLayer', 'ftesting.zcml')

def test_suite():
    suite = unittest.TestSuite()

    suites = (functional.FunctionalDocFileSuite('ftests.txt'),)

    for s in suites:
        s.layer=TestLayer
        suite.addTest(s)
    return suite
