from collective.testing.utils import monkeyAppAsSite
monkeyAppAsSite()

import os, sys, unittest
from zope.testing import doctest
from collective.testing.layer import ZCMLLayer

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

def test_suite():
    import rhizome.five as rhizome
    from Testing.ZopeTestCase import FunctionalDocFileSuite
    testsuite = FunctionalDocFileSuite(
        'README.txt',
        optionflags=optionflags,
        package=rhizome)
    testsuite.layer = ZCMLLayer
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
