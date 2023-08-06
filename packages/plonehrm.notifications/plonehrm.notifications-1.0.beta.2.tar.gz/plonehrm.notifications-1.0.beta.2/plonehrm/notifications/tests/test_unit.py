import unittest
from zope.testing import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('doc/technical.txt',
                             package='plonehrm.notifications'),
        #doctest.DocTestSuite(module='plonehrm.notifications.adapters'),
        ))
