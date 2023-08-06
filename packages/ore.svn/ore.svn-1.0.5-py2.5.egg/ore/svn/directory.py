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
SubversionDirectory
===================

directories use the standard python mapping interface to expose their children.

  >> directory = node # the root is also a directory, alias it for clarity
  >> directory.keys()
  ["zebra.pyx", "libzebra.h", "libzebra.c", "tests"]

  >> directory.files()
  ["zebra.pyx", "libzebra.h", "libzebra.c"]

  >> "readme.txt" in directory
  False

  >> child_nodes = directory.values()
  >> file = directory['zebra.pyx']
  >> directory.get('nonexistant')

$Id: directory.py 2205 2008-05-07 19:44:27Z hazmat $
"""

from zope.interface import implements
from svn import core, fs

from interfaces import ISubversionDirectory, ISubversionFile, ISubversionNode
from node import SubversionObject
from utils import svn_path_join, svn_path_parent

class SubversionDirectory(SubversionObject):
    """
    Subversion Directory Node
    """

    implements( ISubversionDirectory )
    
    def __getitem__(self, key):
        """
        mapping interface for subnode retrieval
        """
        #print 'iget', key
        svn_context = self.getSVNContext()
        resource_ctx = svn_context.getResourceContext()
        path = svn_path_join(self.svn_path, key)

        if fs.is_dir(resource_ctx.root, path, resource_ctx.pool):
            return svn_context.SVNDirectoryFactory(path)
        if fs.is_file(resource_ctx.root, path, resource_ctx.pool):
            return svn_context.SVNFileFactory(path)

        raise KeyError( key )

    def get(self, key, default=None):
        #print 'dget', key        
        try:
            return self.__getitem__( key )
        except KeyError:
            return default

    def keys(self):
        return self.mapNodes( self._getKeys )

    def values(self):
        return list( self.itervalues() )

    def __contains__(self, name):
        ctx = self.getSVNContext().getResourceContext()
        return fs.check_path( ctx.root,
                              svn_path_join(self.svn_path, name),
                              ctx.pool ) and True or False

    def __len__(self):
        return len( self.keys() )

    def itervalues( self ):
        return self.mapNodes( self._getValues ) 

    def _getValues( self, svn_context, resource_ctx, entries ):
        names = entries.keys()
        for name in names:
            entry = entries[name]
            entry_path = svn_path_join( self.svn_path, name )
            if entry.kind == core.svn_node_dir:
                yield svn_context.SVNDirectoryFactory( entry_path )
            elif entry.kind == core.svn_node_file:
                yield svn_context.SVNFileFactory( entry_path )
    
    def iterkeys( self ):
        return iter( self.mapNodes( self._getKeys ) )

    __iter__ = iterkeys

    def _getKeys( self, svn_context, resource_ctx, entries ):
        return entries.keys()

    def mapNodes( self, func ):
        """
        map the given function against the svn entries from this directory
        """
        svn_context = self.getSVNContext()
        revision = svn_context.getRevision()

        svn_context = self.getSVNContext()
        resource_ctx = svn_context.getResourceContext()
        revision = svn_context.getRevision()
        
        entries = fs.dir_entries( resource_ctx.root,
                                  self.svn_path,
                                  resource_ctx.pool)

        return func( svn_context, resource_ctx, entries )

    def getDirectories(self):
        """
        get all the subdirectories of this node
        """
        return [ dn for dn in self.values() if ISubversionDirectory.providedBy( dn )]

    directories = property( getDirectories, doc=getDirectories.__doc__ )
    
    def getFiles(self):
        """
        get all the files in this directory
        """
        return [ fn for fn in self.values() if ISubversionFile.providedBy( fn ) ]

    files = property( getFiles, doc=getFiles.__doc__ )

    # write api
    def __delitem__( self, name ):
        """
        delete a contained node with the given name
        """
        if not self.__contains__( name ):
            raise KeyError( name )
        self._modified()
        svn_path = svn_path_join( self.svn_path, name )
        ctx = self.getSVNContext().getResourceContext()
        fs.delete( ctx.txnroot, svn_path, ctx.pool )

    def __setitem__( self, name, value ):
        """
        move/rename a node, node must already exist in a committed revision
        """
        assert ISubversionNode.providedBy( value )
        svn_path = svn_path_join( self.svn_path, name )
        
        # check that its really a move        
        if svn_path == value.svn_path:  
            return

        self._modified()

        # check if we have an existing node with the same name if so delete it
        # ??? XXX should we do this.. or just raise an error..
        if self.__contains__( name ):
            raise SyntaxError('Existing node with name %s'%name)
            del self[ name ]
        
        # copy into ourselves
        self.copy( name, value )
        
        # delete from existing parent
        svn_ctx = self.getSVNContext()        
        source_parent_path = svn_path_parent( value.svn_path )
        parent_node = svn_ctx.getSVNObject( source_parent_path )
        del parent_node[ value.getId() ]
        return self.get( name )
    
    def makeDirectory( self, name ):
        """
        create a directory and return it
        """
        self._modified()
        ctx = self.getSVNContext().getResourceContext()
        svn_path = svn_path_join( self.svn_path, name )        
        fs.make_dir( ctx.txnroot, svn_path, ctx.pool )
        return self.get( name )

    makedir = makeDirectory
    
    def makeFile( self, name ):
        """
        create an empty file directly and return it
        """
        self._modified()
        ctx = self.getSVNContext().getResourceContext()
        svn_path = svn_path_join( self.svn_path, name )        
        fs.make_file( ctx.txnroot, svn_path, ctx.pool )
        return self.get( name )        

    def copy( self, name, node):
        """
        copy a node into this directory with the given name                
        """
        assert ISubversionNode.providedBy( node )        
        if self.__contains__( name ):
            raise SyntaxError("node w/ name %s already exists"%name)

        svn_path = svn_path_join( self.svn_path, name )
        # copying with same name into ourselves
        if svn_path == node.svn_path: 
            return node
        self._modified()        
        ctx = self.getSVNContext().getResourceContext()
        # svn doesn't currently allow copying from mutable trees, so the node
        # must already exist in a previous revision - current as of svn 1.3.2
        fs.copy( ctx.fsroot, node.svn_path, ctx.txnroot, svn_path, ctx.pool )
        return self.get( name )


    def merge( self, dir_node ):
        """
        given a directory node with a common ancestor as this one, recursively merge
        directory contents, if there are conflict differences, return the name of the
        node causing an error.
        """
        assert ISubversionDirectory.isImplementedBy( dir_node )
        raise NotImplemented

        
