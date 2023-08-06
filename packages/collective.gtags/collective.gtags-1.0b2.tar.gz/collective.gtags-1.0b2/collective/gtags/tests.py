import doctest
import unittest
from zope.testing import doctestunit
from zope.app.testing import setup

def setUp(test):
    pass
        
def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite(
            'tagging.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctestunit.DocFileSuite(
            'behaviors.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))