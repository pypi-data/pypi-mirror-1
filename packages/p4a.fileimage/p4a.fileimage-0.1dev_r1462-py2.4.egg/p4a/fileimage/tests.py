import unittest

from zope.testing import doctest
from zope.component import testing

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('p4a.fileimage._property'),
                               
        doctest.DocFileSuite('file.txt',
                             setUp=testing.setUp,
                             tearDown=testing.tearDown,
                             ),
        ))
