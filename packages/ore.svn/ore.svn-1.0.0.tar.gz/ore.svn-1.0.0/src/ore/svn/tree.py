####################################################################
#    ore.svn
#    Copyright (C) 2002-2006 kapil thangavelu <k_vertigo@objectrealms.net>
#    Copyright (C) 2006 ObjectRealms, LLC
#
#    This product is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This product is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this product; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite
####################################################################
"""
Tree Iterators and Utility Operations for SVN Repositories.

author: kapil thangavelu <hazmat@objectrealms.net>

$Id: tree.py 1594 2006-08-24 00:12:59Z hazmat $
"""
import sys
from svn import fs
from interfaces import ISubversionDirectory, ISubversionFile
from file import SubversionLock

def nodeIterator( root_node, matcher=None):
    """
    an iterator over all nodes below the given root node, if matcher is given and is callable,
    use it to filter returned nodes.
    """
    for node in root_node.values():
        if matcher and not matcher( node ): continue
        if ISubversionDirectory.providedBy( node ):
            yield n
            for n in iterate( node, matcher ):
                yield n
        else:
            yield n
    
def fileIterator( root_node, matcher=None):
    """
    an iterator over all files below the given root node, accepts optional matcher.
    """
    if matcher:
        matcher = FuncFilterChain( matchFile, matcher )
    return nodeIterator( root_node, matcher )

def dirIterator( root_node, matcher=None):
    " an iterator over all directories below the given root node, accepts optional matcher."
    if matcher:
        matcher = FuncFilterChain( matchDir, matcher )
    return nodeIterator( root_node, matcher )    
    
def lockIterator( root_node ):
    # returns locked nodes under the given root, doesn't iterate, just return the list
    ctx = root_node.getResourceContext()
    locks = []
    def collectLocks( lock, pool ):
        locks.append( SubversionLock( lock ) )
    fs.get_locks( ctx.fsptr, root_node.svn_path, collectLocks,  ctx.pool )
    return locks

def lockTree( root_node, token, steal=0 ):
    for node in fileIterator( root_node ):
        node.lock( token, steal )

def unlockTree( root_node, token, break_locks=0 ):
    for node in fileIterator( root_node ):
        node.unlock( token, break_locks )

def printTree(d, stream=sys.stdout, indent=1):
    """ a simple ascii indented tree print of the repository from the given node """
    print >> stream, ' '*(indent-2), d.getId()
    for f in d.files:
        print >> stream, ' '*indent, f.getId()
    print >> stream, ""
    for sd in d.directories:
        printTree(sd, stream, indent+2)

class FuncFilterChain( object ):

    def __init__( self, *callables ):
        self.callables = callables

    def __call__(self, *args, **kw):
        for c in self.callables:
            if not c(*args, **kw):
                return False
        return True

def matchFile( node ):
    return ISubversionFile.providedBy( node )

def matchDir( node ):
    return ISubversionDirectory.providedBy( node )
