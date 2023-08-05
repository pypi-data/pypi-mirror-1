"""
$Id: test_File.py 1628 2006-09-03 02:13:48Z hazmat $
"""

from unittest import TestSuite, makeSuite, TestCase, main
from datetime import datetime

import time
import os
import md5

from _base import SubversionTest
        
class TestSVNFile( SubversionTest ):

    def test_Annotation(self):
        file = self.root['elephants.txt']
        lines =  file.getAnnotatedLines()
        line_rev_map = (4, 1, 2)
        for i in range(len(lines)):
            self.assertEqual( line_rev_map[i], lines[i][0])

    def test_getSize(self):
        file = self.root['elephants.txt']
        content = file.getContents()
        self.assertEqual( file.getSize(), len(content))

    def test_getContents( self ):
        file = self.root['elephants.txt']
        self.assertEqual( file.contents.strip().split('\n')[1:], text_block.strip().split('\n')[1:])
        
    def test_getMD5(self):
        file = self.root['elephants.txt']
        checksum = file.getMD5()
        contents = file.getContents()
        md5sink = md5.new()
        md5sink.update( contents )
        checksum2 = md5sink.hexdigest()
        self.assertEqual( checksum, checksum2)

    def test_write(self):
        file = self.root['elephants.txt']
        file.write( "hello world" )
        self.assertEqual( file.getContents(), "hello world")
        file.write("goodbye")
        self.assertEqual( file.contents, "goodbye")

    def test_writeStream( self ):
        temp_file = os.tmpfile()
        temp_file.write("roses are red")
        temp_file.seek(0)

        file = self.root['elephants.txt']
        file.writeStream( temp_file )
        self.assertEqual( file.contents, 'roses are red')

    def XXXtest_getDiff(self):
        output = self.root['elephants.txt'].getDiff( 4, 2)
        print "Diff"
        print output
        print "html diff"
        writer = DiffWriter()
        output = self.root['elephants.txt'].getDiff( 4, 2)
        writer.close()
        print writer.getvalue()

    def test_Locking(self):
        # lock and unlock
        self.ctx.setAccess("ore.svn.test")

        node = self.ctx.root['elephants.txt']
        lock = node.lock()
        
        self.assertEqual( lock.path, '/core/elephants.txt')
        self.assertEqual( lock.owner, 'ore.svn.test')
        self.assertEqual( lock.expiration_date, None )
        self.assertTrue(  lock.token.startswith('opaquelocktoken') )
        self.assertEqual( lock.comment, '')
        
        node.unlock()
        self.assertEqual( node.locked, None )

        
text_block = """\
$Id: test_File.py 1628 2006-09-03 02:13:48Z hazmat $
smart animals
revision 2"""

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSVNFile))
    return suite

if __name__ == '__main__':
    main()

    

    


        
