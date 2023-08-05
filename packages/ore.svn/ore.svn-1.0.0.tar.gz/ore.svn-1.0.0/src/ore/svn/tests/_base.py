"""
$Id: _base.py 1532 2006-08-07 10:45:40Z hazmat $
"""
import os
import transaction
from unittest import TestCase

from ore.svn import SubversionContext

test_home = os.path.join( os.path.abspath(os.path.dirname( __file__ )) )
test_repo_path = os.path.join( test_home, 'testrepo')

class SubversionTest( TestCase ):

    def setUp( self ):
        self.ctx = SubversionContext(test_repo_path, '/core')
        self.root = self.ctx.getSVNRootObject()
        
    def tearDown( self ):
        transaction.abort()        
        del self.root
        self.ctx.clear()
        del self.ctx


    

    
