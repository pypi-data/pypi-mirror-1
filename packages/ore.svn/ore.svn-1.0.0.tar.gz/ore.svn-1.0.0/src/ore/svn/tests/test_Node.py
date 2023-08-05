"""
$Id: test_Node.py 1587 2006-08-22 20:24:29Z hazmat $
"""

from unittest import TestSuite, makeSuite, TestCase, main
from datetime import datetime

import time
import os

from _base import SubversionTest

class TestSVNNode( SubversionTest ):


    def test_nodeLog(self):
        entries = self.root['elephants.txt'].getLogEntries()
        self.assertEqual(len(entries), 3 )
        entries = self.root['cats.txt'].getLogEntries()
        revisions = (1,2,3)
        for i in entries:
            self.assertEqual( i.author, 'hazmat')
            assert i.revision in revisions
            
        self.assertEqual(len(entries), 3)

    def test_nodeLogPaths(self):
        # getting changed path info is broken, can cause segfaults
        # if change info for a given path is looked at.
        entries = self.root.getLogEntries(changed_paths=1)
        self.assertEqual(len(entries), 5)
        
    def test_RevisionPathMap( self ):
        rev_map = self.root['resources']['icon.png'].getRevisionPathMap(cross_copies=1)

        map = { 1:'/core/svn_file.png',
                3:'/core/icon.png',
                5:'/core/resources/icon.png' }

        self.assertEqual(len(rev_map), 3)
        for mk in map.keys():
            assert mk in rev_map
            self.assertEqual( map[mk], rev_map[mk] )
        
    def test_getLog(self):
        file = self.root['elephants.txt']
        log = file.getLog()
        self.assertEqual(log.author, 'hazmat')
        self.assertEqual(log.message, 'add props and line\n')

    def ztest_getRevisionForDate(self):
	svn_context = self.root.getSVNContext()
	revision = svn_context.getRevisionForDate( time.time() )
        self.assertEqual( revision, 5 )

        revision = svn_context.getRevisionForDate( 1000000 )
        self.assertEqual( revision, 0 )

    def test_setRevision(self):
        self.ctx.setRevision( revision=1 )
        # now test that a call to set revision with no argswill reset us to the latest
        self.ctx.setRevision( None )
        root = self.ctx.getSVNRootObject()
        self.assertEqual( len(root.getFiles()), 2)

    def test_getRevisionInfo(self):
        info = self.ctx.getRevisionInfo()
        self.assertEqual( len(info.paths), 3)

    def test_getRevisionByDate(self):
        dt = datetime.now()
        rev = self.ctx.getRevisionByDate( dt )
        self.assertEqual( rev, 5 )


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSVNNode))
    return suite

if __name__ == '__main__':
    main()

    

    


        
