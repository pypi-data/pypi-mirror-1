import unittest
from zope.testing import doctest
import _base

def wrapper( test ):
    _base.setUp( test )

def test_suite():

    d = dict( test_repo_path = _base.test_repo_path )
    
    return unittest.TestSuite((
        doctest.DocFileSuite(
            '../readme.txt',
            setUp=wrapper,
            tearDown=_base.tearDown,
            globs = d,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS            
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
