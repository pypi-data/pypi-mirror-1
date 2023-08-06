"""
$Id: test_Transaction.py 2196 2008-05-06 03:52:38Z hazmat $
"""

from unittest import TestSuite, makeSuite, main

import transaction
from ore.svn.interfaces import ISubversionFile
from _base import SubversionTest

class TestSVNTransaction( SubversionTest ):

    def test_abort(self):
        self.root.makeDirectory('bricks')
        self.assertTrue( 'bricks' in self.root )
        transaction.abort()
        self.assertFalse( 'bricks' in self.root )
        
    def test_commit(self):
        node = self.root.makeFile('white-elephants.txt')
        transaction.commit()
        self.root.copy( 'mongoose.txt', node )        
        self.assertTrue( 'mongoose.txt' in self.root )
        transaction.abort()
        
    def test_txnapi( self ):
        txn =  self.ctx.transaction
        node = self.root.makeFile('white-elephants.txt')
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

    

    


        
