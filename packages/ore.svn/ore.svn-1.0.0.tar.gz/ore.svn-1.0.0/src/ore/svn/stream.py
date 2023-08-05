"""
file handle abstraction for svn nodes
$Id: stream.py 1648 2006-09-05 08:19:11Z hazmat $
"""

from cStringIO import StringIO

class FileStream( object ):

    def __init__(self, file, mode="r" ):
        self.file = file
        self.stream = StringIO( file.contents )
        self.changed = False
        self.closed = False
        self.mode = mode
        
    def read( self, size=-1):
        if self.closed:
            raise ValueError("I/O operation on closed file")
        return self.stream.read( size )

    def close( self ):
        self.flush()
        self.closed = True
        self.node = None
        del self.stream
        
    def seek( self, offset, whence=0):
        if self.closed:
            raise ValueError("I/O operation on closed file")
        return self.stream.seek( offset, whence )

    def tell( self ):
        if self.closed:
            raise ValueError("I/O operation on closed file")        
        return self.stream.tell()

    def flush( self ):
        if self.closed:
            raise ValueError("I/O operation on closed file")        
        if self.changed:
            self.node.contents = self.stream.getvalue()
            self.changed = False

    def write( self, data ):
        if self.closed:
            raise ValueError("I/O operation on closed file")
        self.stream.write( data )
