import os
import unittest
from zope.testing import doctest

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def setUp(test):
    tests_dir = os.path.dirname(__file__)
    stripdupes_script = os.path.join(
        os.path.dirname(os.path.dirname(tests_dir)),
        'bin', 'stripdupes')
    test.globs.update(stripdupes_script=stripdupes_script)

def test_suite():
    return doctest.DocFileSuite(
        'README.txt', setUp=setUp, optionflags=optionflags)
        
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
