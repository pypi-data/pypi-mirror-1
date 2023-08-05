"""
$Id: test_Directory.py 1532 2006-08-07 10:45:40Z hazmat $
"""

from unittest import TestSuite, makeSuite, TestCase, main
from datetime import datetime

import time
import os
import md5

from ore.svn import SubversionContext
from ore.svn.interfaces import ISubversionDirectory, ISubversionFile

from _base import SubversionTest
        
class TestSVNDirectory( SubversionTest ):

    def test_keys(self):
        self.assertEqual(len(self.root.keys()), 3)

    def test_values(self):
        self.assertEqual(len(self.root.values()), 3 )

    def test_len( self ):
        self.assertEqual( len( self.root ), 3 )

    def test_delitem(self):
        del self.root['elephants.txt']
        self.assertEqual( 'elephants.txt' in self.root, False )
        
    def test_copy(self):
        node = self.root['elephants.txt']
        self.root.copy( 'mongoose.txt', node )
    
    def test_setitem(self):
        node = self.root['resources']['icon.png']
        self.root[ 'zebra.png' ] = node
        self.assertTrue( ISubversionFile.providedBy( self.root['zebra.png'] ) )
    
    def test_makeDirectory(self):
        self.root.makeDirectory('noisy')
        self.assertTrue( ISubversionDirectory.providedBy( self.root['noisy']  ) )
        
    def test_makeFile(self):
        self.root.makeFile('noisy.txt')
        self.assertTrue( ISubversionFile.providedBy( self.root['noisy.txt'] ) )

    def test_contains(self):
        not_contained = 'mongoose.txt' in self.root
        self.assertEqual( not_contained, False  )
        contained = 'elephants.txt'in self.root
        self.assertEqual( contained, True )        
        
    def test_getFiles(self):
        files = self.root.files
        self.assertEqual( len(files), 2)
        file_set_head = ['cats.txt', 'elephants.txt']
        for f in files:
            truth = f.getId() in file_set_head
            self.assertEqual(truth, 1)

    def test_getFilesInitialRevision(self):
        self.ctx.setRevision( revision=1 )
        self.root = self.ctx.getSVNRootObject()
        files = self.root.getFiles()
        self.assertEqual( len(files), 3)
        file_set_head = ['rabbits.txt', 'svn_file.png','elephants.txt']
        for f in files:
            truth = f.getId() in file_set_head
            self.assertEqual(truth, 1)

    def test_getDirectories(self):
        self.assertEqual( len(self.root.getDirectories()), 1)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSVNDirectory))
    return suite

if __name__ == '__main__':
    main()

    

    


        
