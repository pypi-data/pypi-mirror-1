####################################################################
# Copyright 2002-2008 Kapil Thangavelu <kapil.foss@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
####################################################################
"""
file handle abstraction for svn nodes
$Id: stream.py 2205 2008-05-07 19:44:27Z hazmat $
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
