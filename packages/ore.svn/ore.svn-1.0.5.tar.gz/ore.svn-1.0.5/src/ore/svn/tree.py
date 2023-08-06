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
Tree Iterators and Utility Operations for SVN Repositories.

author: kapil thangavelu <hazmat@objectrealms.net>

$Id: tree.py 2205 2008-05-07 19:44:27Z hazmat $
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
            yield node
            for n in nodeIterator( node, matcher ):
                yield n
        else:
            yield node
    
def fileIterator( root_node, matcher=None):
    """
    an iterator over all files below the given root node, accepts optional matcher.
    """
    if matcher:
        matcher = FuncFilterChain( matchFile, matcher )
    else:
        matcher = matchFile
    return nodeIterator( root_node, matcher )

def dirIterator( root_node, matcher=None):
    " an iterator over all directories below the given root node, accepts optional matcher."
    if matcher:
        matcher = FuncFilterChain( matchDir, matcher )
    else:
        matcher = matchDir
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
