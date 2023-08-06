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
Subversion File Nodes
=====================

in addition to the svnnode log inspection, files offer some basic diff methods
and content writing abilities.
  >> file.contents
  >> file.write("hello world")
  >> file.size
  >> file.checksum
  >> file.mime_type

Location and History
 
all nodes have an api for discovering their path ancestry with the corresponding
revision information.  

??? new name
 >> file.getMappedLogEntries()


$Id: file.py 2205 2008-05-07 19:44:27Z hazmat $
"""

import difflib, time
from zope.interface import implements
from svn import core, fs, delta
from utils import format_size, charbuffer, make_time, make_aprtime

from interfaces import ISubversionFile, CHUNK_SIZE
from node import SubversionObject
from stream import FileStream

class SubversionFile(SubversionObject):
    """
    Subversion File Node
    """

    implements( ISubversionFile )
    
    def getMimeType(self):
        """
        get the mime type of this file node if set, if not return
        text/plain
        """
        mime_type = self.getProperty(core.SVN_PROP_MIME_TYPE)
        if mime_type is None:
            return 'text/plain'        
        return mime_type
    
    def setMimeType( self, value ):
        assert isinstance( value, str )
        self.setProperty( core.SVN_PROP_MIME_TYPE, value )

    contentType = mime_type = property( getMimeType, setMimeType, doc=getMimeType.__doc__ )

    def getContents(self, revision=None, writer=None):
        """
        get the contents of the file node, if writer is provide, it should
        be a file handle like interface to which the contents of the file
        will be streamed, else the entire file contents will be returned
        as a string.
        """
        rval = not writer
        svn_context = self.getSVNContext()

        resource_ctx = svn_context.getResourceContext()

        if revision is not None and isinstance(revision, int):
            resource_ctx.setRevision( revision )

        stream = fs.file_contents( resource_ctx.root,
                                   self.svn_path,
                                   resource_ctx.pool )

        if writer is None:
            writer = charbuffer()

        while 1:
            data = core.svn_stream_read(stream, CHUNK_SIZE)
            if not data:
                break
            writer.write(data)

        if rval:
            return writer.getvalue()

    read = getContents

    def getMD5(self):
        """ returns the md5 checksum of the file's contents """
        ctx = self.getSVNContext().getResourceContext()
        return fs.file_md5_checksum( ctx.root, self.svn_path, ctx.pool )

    checksum = property( getMD5, doc=getMD5.__doc__ )

    def getSize(self, pretty=0):
        """
        return the size of the file node in bytes
        """
        svn_context = self.getSVNContext()
        resource_ctx = svn_context.getResourceContext()
        size = fs.file_length(resource_ctx.root, self.svn_path, resource_ctx.pool)
        if pretty:
            return format_size( size )
        return size

    size =  property( getSize, doc=getSize.__doc__ )
    
    def getAnnotatedLines(self, revision_set=(), include_copies=1):
        """
        perform a diff of the file node contents, returns an array
        of ( line number, (revision, line content, author ) ).
        
        revision set if passed in, should be revisions that the content
        was changed in, only these revisions will be considered, else
        all revisions the content was altered in will be considered.

        if included copies is true than cross copy history when finding
        revisions to include in diff.
        """
        stime = time.time()
        svn_context = self.getSVNContext()
        origin_rev  = svn_context.getRevision()
        annotations = []
        contents = ''

        revision_path_map = self.getRevisionPathMap( include_copies )

        if not revision_set:
            revision_set = revision_path_map.keys()

        # set revision order low high
        revision_set.sort()
        # flush mem.
        resource_ctx = svn_context.getResourceContext() #initialize(revision_set[-1])

        if not len(revision_set) > 1 or self.isBinary():
            return ()

        pool = core.svn_pool_create(resource_ctx.pool)
        
        try:
            for r in revision_set:
                revision_root = fs.revision_root(resource_ctx.fsptr, r, pool)
                
                rev_author = fs.revision_prop(resource_ctx.fsptr,
                                              r,
                                              core.SVN_PROP_REVISION_AUTHOR,
                                              pool) or ''
                
                stream = fs.file_contents(revision_root,
                                          revision_path_map[r],
                                          pool)
                buffer = charbuffer()

                while 1:
                    data = core.svn_stream_read(stream, CHUNK_SIZE)
                    if not data:
                        break
                    buffer.write(data)

                previous_contents = contents
                contents = buffer.getvalue()
                delta = difflib.ndiff(
                    previous_contents.splitlines(1),
                    contents.splitlines(1)
                    )

                # annotate algorithm
                li = 0
                for d in delta:
                    flag = d[0]
                    if flag == ' ':
                        li += 1
                        continue
                    elif flag == '?':
                        continue
                    elif flag == '+':
                        annotations.insert(li, (r, d[2:], rev_author) )
                        li += 1
                    elif flag == '-':
                        del annotations[li]

                fs.close_root(revision_root)
        finally:
            core.svn_pool_clear(pool)
            core.svn_pool_destroy(pool)

        # reset the context revision 
        svn_context.setRevision(origin_rev)
        
        return [annotations[i] for i in xrange(len(annotations))]


    def write( self, value ):
        """ write the value to the file's contents """
        if not isinstance(value, (str, unicode)):
            raise RuntimeError("can only write strings to files")
        if isinstance( value, unicode ):
            value = value.encode('utf-8')
        
        self._modified()
        ctx = self.getSVNContext().getResourceContext()
        handler, baton = fs.apply_textdelta( ctx.txnroot, self.svn_path, None, None)
        delta.svn_txdelta_send_string( value, handler, baton )

    contents = data = property( getContents, write, doc="contents of file")
    
    def writeStream( self, stream ):
        """ replace the file's contents with that of the streams, stream contents
        should be utf-8 encoded for i18n, unicode strings won't work."""
        self._modified()
        ctx = self.getSVNContext().getResourceContext()
        handler, baton = fs.apply_textdelta( ctx.txnroot, self.svn_path, None, None)
        delta.svn_txdelta_send_stream( stream, handler, baton )

    def lock( self, token=None, comment='', expiration_date=0, steal=False ):
        """
        lock the node to prevent modification by other users, lots of interesting
        caveats ;-). first is you must have an a user access set on the SubversionContext,
        this api allows you to steal another user's lock, which in affect removes their lock,
        and adds a lock for the current user. finally as of SVN 1.2, the api works only for files.

        the lock api operates outside of transaction boundaries! this is useful but is also
        an important caveat.
        """

        ctx = self.getSVNContext().getResourceContext()

        if not ctx.access:
            raise SyntaxError( "repository access must be set .. see ctx.setAccess" )
        
        if not steal:
            if self.locked:
                raise SyntaxError("node is already locked")

        if ( token is not None ) and ( not isinstance( token,  str ) ):
            raise SyntaxError("Invalid Token %r"%token)

        if expiration_date is not 0:
            expiration_date = make_aprtime( expiration_date )
        
        lock = fs.lock( ctx.fsptr,
                        self.svn_path,
                        token,
                        comment,
                        False,
                        expiration_date,
                        ctx.revision, # only allow locking the most recent rev
                        bool(steal),
                        ctx.pool )

        # add the lock token to the access, so the current access can do things with the
        # given locked node.
        fs.access_add_lock_token( ctx.access, lock.token )
        
        return SubversionLock( lock )

    def unlock(self, token=None, break_lock=False): #, associate=True):
        """
        unlock the node to allow modification by others, by default only allows breakage
        if your the owner, unless break_lock is true, in which case user context is
        ignored, and the lock is removed.

        if the node is not locked, this operation is a noop.
        
#        if break lock is false and if associate is true, attempt to discover if the current
#        access user owns an existing lock, and transparently associate it with the access before
#        unlocking.
        
        the lock api operates outside of transaction boundaries! this is useful but is also
        an important caveat.
        """
        ctx = self.getSVNContext().getResourceContext()
        if break_lock is False and ctx.access is None:
            raise SyntaxError("repository access must be set .. see ctx.setAccess")

        lock = self.locked
        
        # not locked
        if lock is None: 
            return
        
        # associate with current access
        #if break_lock is False and associate and lock:
        #    fs.access_add_lock_token( ctx.access, lock.token )

        # unlock
        if token is None:
            token = lock.token
            
        fs.unlock( ctx.fsptr, self.svn_path, token, bool(break_lock), ctx.pool )
        
    def _isLocked( self ):
        """
        is the node locked
        """
        ctx = self.getSVNContext().getResourceContext()
        svn_lock = fs.get_lock( ctx.fsptr, self.svn_path, ctx.pool )
        if not svn_lock:
            return None
        return SubversionLock( svn_lock )

    locked = property( _isLocked, doc = _isLocked.__doc__ )

    def open( self, mode="r"):
        return FileStream( self, mode )

class SubversionLock( object ):

    __slots__ = ( 'path', 'token', 'owner', 'comment', 'creation_date', 'expiration_date')

    def __init__( self, svn_lock ):
        self.path = svn_lock.path
        self.token = svn_lock.token
        self.owner = svn_lock.owner
        self.comment = svn_lock.comment
        self.creation_date = make_time( svn_lock.creation_date )
        self.expiration_date = svn_lock.expiration_date and \
                               make_time( svn_lock.expiration_date ) \
                               or None
    def __repr__(self):
        return "<SVNLock by %s on %s created %s>"%(self.owner, self.path, self.creation_date)
