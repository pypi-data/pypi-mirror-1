import unittest
from zope.testing import doctest

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=(
            doctest.ELLIPSIS|
            doctest.NORMALIZE_WHITESPACE|
            doctest.REPORT_NDIFF))
        
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
