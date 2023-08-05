"""
$Id: test_Transaction.py 1533 2006-08-07 11:22:07Z hazmat $
"""

from unittest import TestSuite, makeSuite, TestCase, main
from datetime import datetime

import time
import os
import md5
import transaction
import shutil

from ore.svn import SubversionContext
from ore.svn.interfaces import ISubversionDirectory, ISubversionFile
from ore.svn import repos

test_home = os.path.join( os.path.abspath(os.path.dirname( __file__ )) )
test_repo_path = os.path.join( test_home, 'testrepo')

svn_txn_repo = "svntxnrepo"

class TestSVNTransaction( TestCase ):

    def setUp( self ):
        if os.path.exists( svn_txn_repo ):
            shutil.rmtree( svn_txn_repo )
        self.ctx = repos.copy( test_repo_path, svn_txn_repo )
        self.root = self.ctx.getSVNRootObject()                

    def tearDown(self):
        transaction.abort()                
        del self.root
        self.ctx.clear()
        del self.ctx
        repos.destroy( svn_txn_repo )

    def test_abort(self):
        self.root.makeDirectory('bricks')
        self.assertTrue( 'bricks' in self.root )
        transaction.abort()
        self.assertFalse( 'bricks' in self.root )
        
    def test_commit(self):
        node = self.root.makeFile('elephants.txt')
        transaction.commit()        
        self.root.copy( 'mongoose.txt', node )        
        self.assertTrue( 'mongoose.txt' in self.root )
        transaction.abort()
        
    def test_txnapi( self ):
        txn =  self.ctx.transaction
        node = self.root.makeFile('elephants.txt')
        txn.author = "kapil"
        txn.message = "hello world"
        txn.commit()
        self.assertEqual(self.ctx.getRevisionInfo().author, "kapil")

        node = self.root.makeDirectory('world')
        txn.author = "ben"
        txn.message = "meet world"        
        txn.commit()
        self.assertEqual( self.ctx.getRevisionInfo().author, "ben")

    def xtest_lockstatus(self):
        node = self.root['resources']['icon.png']
        self.root[ 'zebra.png' ] = node
        self.assertTrue( ISubversionFile.providedBy( self.root['zebra.png'] ) )
    

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSVNTransaction))
    return suite

if __name__ == '__main__':
    main()

    

    


        
