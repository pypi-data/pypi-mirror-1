import unittest
from zope.testing import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('doc/technical.txt',
                             package='plonehrm.notifications',
                             optionflags=OPTIONFLAGS),
        #doctest.DocTestSuite(module='plonehrm.notifications.adapters'),
        ))
