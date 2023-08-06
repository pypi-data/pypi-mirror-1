import unittest
from zope.testing import doctest

from rpatterson.mailsync import testing

def test_suite():
    return doctest.DocFileSuite(
        'watch.txt',
        setUp=testing.setUp, tearDown=testing.tearDown,
        optionflags=(
            doctest.ELLIPSIS|
            doctest.REPORT_NDIFF))
        
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
