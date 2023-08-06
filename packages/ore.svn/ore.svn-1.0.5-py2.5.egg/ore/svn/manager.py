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
Subversion Data Manager to integrate with zope transactions.


dev notes.

 - we don't, really need to lock all nodes for pessimistic behavior, just the lcd
   parent nodes for the txn node set.

$Id: manager.py 2205 2008-05-07 19:44:27Z hazmat $
"""

import weakref

import transaction
from zope.interface import implements
from transaction.interfaces import IDataManager

from interfaces import ISubversionDirectory, NoTransaction
from svn import core, fs as svn_fs
from property import txn_property

import tree

class SubversionTransaction( object ):
    """
    a user consumable facade to the data manager, we bind to the
    resource context, to allow for easy usage across transactions
    boundaries.
    """

    __slots__ = ("_ctx",)
    
    def __init__( self, resource_ctx):
        self._ctx = weakref.ref( resource_ctx )

    def _get_dm(self):
        dm = self._ctx().getDataManager()
        if not dm or not dm.svnfs_txn:
            raise NoTransaction("no active transaction")
        return dm

    dm = property( _get_dm )
    
    def commit( self ):
        self.dm.svnfs_txn # check the transaction
        transaction.commit()
        
    def abort( self ):
        self.dm.svnfs_txn # check the transaction
        transaction.abort()

    author = txn_property( core.SVN_PROP_REVISION_AUTHOR )
    message = txn_property( core.SVN_PROP_REVISION_LOG )
    
class SubversionDataManager( object ):

    implements( IDataManager )

    def __init__( self, resource_ctx ):
        self.resource_ctx = resource_ctx

        # lock modifications require an fs access set, if one wasn't explicitly
        # set on the resource context, then set one based on the current process username
##         if self.resource_ctx.access is None:
##             if self.resource_ctx.access_name:
##                 self.resource_ctx.setAccess( access_name )
##             else:
##                 self.resource_ctx.setAccess( "ore.svn" )

        self.svnfs_txn = None # svn fs transaction
        self.nodes = set() # modified nodes
        self.lock_token = None # svn fs lock token
        
    def do_nothing( self, *args): pass
    tpc_begin = tpc_vote = do_nothing

    def commit( self, transaction ):
        # called during tpc to do work
        if not self.svnfs_txn:
            return
        # acquire svn locks on nodes we're modifying that aren't already locked
        self._acquireLocks()

    def tpc_finish( self, transaction ):
        # called to finalize work.. don't throw an exception.. last chance for that is tpc_vote
        if self.svnfs_txn:
            # won't call repository hooks
            results = svn_fs.commit_txn( self.svnfs_txn,  self.resource_ctx.pool )
            # clean up our locks
            self._releaseLocks()
        self._clear()
        
    def tpc_abort( self, transaction ):
        if self.svnfs_txn:
            svn_fs.abort_txn( self.svnfs_txn,  self.resource_ctx.pool )        
            self._releaseLocks()
        self._clear()
        
    def abort( self, transaction ):
        if self.svnfs_txn:
            # kill the underlying svn fs transaction
            svn_fs.abort_txn( self.svnfs_txn,  self.resource_ctx.pool )
            # called before locks acquired, no lock cleanup needed
        self._clear()

    def sortKey( self ):
        return "ore.svn-1"

    ########################################
    # api for nodes to register with the transaction when modified
    def register( self, node ):
        self.nodes.add( node )
        # if we haven't already begun svn fs txn.. do so now
        if not self.svnfs_txn:
            self._begin()

    def registerForTxn( self ):
        # the txn is having wierd semantics, sometimes it stays around, and sometimes
        # it disappears, in the former joining blindly adds duplicate txn calls, in the
        # latter it means we don't get txn messages, introspect the txn and find out
        # register based on its state.
        transaction.get().join( self )

    ########################################
    # svn transaction property management
    def getProperties( self ):
        if not self.svnfs_txn:
            raise RuntimeError("no transaction in progress")
        return svn_fs.txn_proplist( self.svnfs_txn )

    def setProperty( self, property_name, property_value ):
        if not self.svnfs_txn:
            raise RuntimeError("no transaction in progress")
        svn_fs.change_txn_prop(  self.svnfs_txn, property_name, property_value, self.resource_ctx.pool )

    def getProperty( self, property_name ):
        if not self.svnfs_txn:
            raise RuntimeError("no transaction in progress")
        return svn_fs.txn_prop( self.svnfs_txn, property_name, self.resource_ctx.pool )

    def delProperty( self, property_name ):
        if not self.svnfs_txn:
            raise RuntimeError("no transaction in progress")
        self.setProperty( property_name, None )
    
    ########################################
    # internals... 

    def _clear( self ):
        self.svnfs_txn = None        
        self.resource_ctx.locked = False
        self.resource_ctx.clearDetails()
        self.resource_ctx.setRevision() # increment the context revision to the latest
        self.resource_ctx = None
        self.nodes = set()
        self.lock_token = None
        
    def _begin(self):
        # lock the resource context during transactions to prevent switching the
        # active context revision.

        self.resource_ctx.locked = True

        # begin an fs transaction
        self.svnfs_txn = svn_fs.begin_txn2( self.resource_ctx.fsptr,
                                            self.resource_ctx.revision,
                                            svn_fs.SVN_FS_TXN_CHECK_LOCKS,
                                            self.resource_ctx.pool )
        
        # setup the transaction root for mutation apis
        self.resource_ctx.txnroot = svn_fs.txn_root( self.svnfs_txn,
                                                     self.resource_ctx.pool )

        # set the revision author to the access name if we have one
        if self.resource_ctx.access is not None:
            self.setProperty( core.SVN_PROP_REVISION_AUTHOR, self.resource_ctx.access_name)

    # locking for pessimistic behavior from svn
    def _releaseLocks(self):
        if self.lock_token is None:
            return
        
        for n in self.locks:
            svn_fs.unlock( n, self.lock_token )

        self.lock_token = None
        self.locks = set()
    
    def _acquireLocks(self):
        return

        # this needs some more thought, for any node, we need to lock all the
        # child nodes, and  we shouldn't lock new nodes, try to allocate
        # just one token, for the lock set. regardless of txn state, we need
        # to unlock all nodes. things become more interesting if we expose
        # locks to the user api.
        
        # what about locks on deleted items.. need to be cleaned up as well
        
        self.lock_token = svn_fs.generate_lock_token( self.resource_ctx.fsroot,
                                                      self.resource_ctx.pool )
        svn_fs.add_lock_token( self.resource_context.access, self.lock_token )
                               
        for n in self.nodes:
            if n is None:
                continue
            n_lock = svn_fs.lock( self.resource_ctx.fsroot,
                                  n.svn_path,
                                  self.lock_token,
                                  u"ztxn",
                                  0, # dav comment
                                  0, # expiration date
                                  self.resource_ctx.revision, # current_rev tests date
                                  0,  # steal lock
                                  self.resource_ctx.pool 
                                  )

            # store the path, with this and the token we can unlock
            self.locks.add( n.svn_path )

            if ISubversionDirectory.providedBy( n ):
                tree.lockTree( n, self.lock_token )
                         

