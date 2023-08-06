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
SubversionNode 
==============

base class for file and directories, handles property management and log inspection

repository revision properties on nodes are accessible via attributes
  >> node.last_log # information from the last 
  >> node.modification_time

node properties are accessible via a mutable properties mapping object

  >> node.properties['svn:externals'] = "ore.svn https://svn.objectrealms.net/svn/public/ore.svn"
 
$Id: node.py 2205 2008-05-07 19:44:27Z hazmat $
"""
from datetime import datetime

from log import SubversionLogEntry
from zope.interface import implements
from svn import core, fs, repos
from utils import svn_path_join

from interfaces import ISubversionNode
from property import PropertyMapping
from log import SVNLogFactory, SVNLogCollection

class SubversionObject( object ):

    implements( ISubversionNode )
    
    def __init__(self, id=None, svn_path=None, __parent__=None):
        self.id = self.__name__ = id
        self.svn_path = svn_path
        self.__parent__ = __parent__

    def getPath( self ):
        return self.svn_path

    path = property( getPath )
    
    def getResourceContext( self ):
        return self.getSVNContext().getResourceContext()

    def getSVNContext( self ):
        return self.__parent__
    
    def getId(self):
        return self.id

    def getNodeId(self):
        """
        Return the Subversion Node Id
        """
        svn_ctx = self.getSVNContext()
        resource_ctx = svn_ctx.getResourceContext()
        uid = fs.node_id(resource_ctx.root, self.svn_path, resource_ctx.pool)
        return '%s'%fs.unparse_id(uid, resource_ctx.pool)

    node_id = property( getNodeId, doc=getNodeId.__doc__ )
    
    def getLog(self, revision=None):
        """ 
        Return A Log Entry Object for A Single Revision. If Revision
        is not specified then the revision is the latest available.
        """
        svn_ctx = self.getSVNContext()
        resource_ctx = svn_ctx.getResourceContext()
        
        if revision is None:
            revision = fs.node_created_rev(resource_ctx.root,
                                           self.svn_path,
                                           resource_ctx.pool)
            # tis a new resource revision on txn we haven't committed, display the appropriate
            # log using information gleaned from the current txn.
            if -1 is revision:
                assert resource_ctx.txnroot is not None, "unknown revision without transaction"
                revision = svn_ctx.revision + 1
                txn = svn_ctx.transaction
                return SubversionLogEntry( author=txn.author,
                                           message=txn.message,
                                           revision=revision,
                                           date=datetime.now() )
                
        return SVNLogFactory(resource_ctx.fsptr, revision, resource_ctx.pool)

    last_log = property( getLog, doc=getLog.__doc__ )
    
    def getModificationTime(self):
        """
        return the last time this node was modified, if pretty_delta
        is true then return the modification as something human readable.
        """
        log = self.getLog()
        return log.date

    modification_time = property( getModificationTime, doc=getModificationTime.__doc__ )
    
    def getLogEntries(self, changed_paths=0, strict_history=False, start_revision=None, end_revision=0):
        """
        get all log entries associated with this node

        if changed paths is true, then find out information on which paths
        changed in the revision.

        start_revision - if specified an integer denoting, it not specified
        the latest revision will be used.

        end_revision - the last revision to return information for.

        the relative sort order of start and end revision determines the
        order log entries are returned in. ie start > end, means reverse
        descending.
        
        if strict_history is true then don't study copy history

        the svn api tends to segfault on careful inspection of paths changed prior to svn 1.3
        """

        svn_ctx = self.getSVNContext()
        resource_ctx = svn_ctx.getResourceContext()
        collection = SVNLogCollection()

        if start_revision is None:
            start_revision = resource_ctx.revision

        strict_history = not not strict_history

        pool = core.svn_pool_create(resource_ctx.pool)
        
        try:
            repos.svn_repos_get_logs(
                resource_ctx.repository,  # repository
                [self.svn_path],          # paths
                start_revision,           # start revision
                end_revision,             # end revision (for sort)
                changed_paths,            # discover changed paths 
                strict_history,           # strict node history (if true)
                collection.addLog,        # receiver
                pool)
        finally:
            #core.svn_pool_destroy( pool )
            pass
        

        return collection.getLogs()

    def getMappedLogEntries(self):
        """
        get all log entries associated with this node, and get the path
        this node was at for each revision log.
        """
        entries = self.getLogEntries()
        rev_map = self.getRevisionPathMap(cross_copies=1)
        for e in entries:
            e.rev_path = rev_map[e.revision]
        return entries

    def getParent(self):
        """
        get the parent object of this node
        """
        svn_ctx = self.getSVNContext()
        segments = self.svn_path.split('/')
        segments.pop(-1)
        svn_parent_path = svn_path_join(*segments)
        return svn_ctx.getSVNObject(svn_parent_path)

    #__parent__ = property( getParent )
    parent_node = property( getParent, doc=getParent.__doc__ )
    
    def getProperty(self, property_name): 
        """
        retrieve a given property name
        """
        svn_ctx = self.getSVNContext()
        revision = svn_ctx.getRevision()

        resource_ctx = svn_ctx.getResourceContext()
        value = fs.node_prop(resource_ctx.root,   # root
                             self.svn_path,       # path 
                             property_name,       # prop name
                             resource_ctx.pool    # pool
                             )
        return value

    def getProperties(self):
        """
        return a mapping of properties on this node. changes to the mapping have no
        effect atm, property mutation should be done through the setProperty api.
        """
        svn_ctx = self.getSVNContext()
        revision = svn_ctx.getRevision()
        
        resource_ctx = svn_ctx.getResourceContext()
        properties =  fs.node_proplist(resource_ctx.root,
                                       self.svn_path,
                                       resource_ctx.pool)
        return properties

    def _getPropertyMapping( self ):
        if self._property_mapping is None:
            self._property_mapping = PropertyMapping( self )
        return self._property_mapping        
    
    _property_mapping = None # cache the property mapping
    properties =  property( _getPropertyMapping, doc="Mutable svn property mapping" )
    
    def setProperty( self, property_name, property_value ):
        """ add or update a subversion property with the given arguments.
        """
        self._modified()
        svn_ctx = self.getSVNContext()
        resource_ctx = svn_ctx.getResourceContext()
        
        fs.change_node_prop( resource_ctx.txnroot,
                             self.svn_path,
                             property_name,
                             property_value,
                             resource_ctx.pool )

    def delProperty( self, property_name ):
        """ delete the subversion property with the given name.
        """
        self._modified()
        self.setProperty( property_name, None )
    
    def getRevisionPathMap(self, cross_copies=0, stop_after_revision=None, limit=None ):
        """
        for every revision this node was modified return a dictionary
        mapping each revision to the path the node was at.

        if stop_after_revision arg is given, then stop after the first
        rev smaller then the given rev.

        # new in 1.1 svn_repos_trace_node_locations
        """
        svn_context = self.getSVNContext()
        resource_ctx = svn_context.getResourceContext()
        pool = core.svn_pool_create(resource_ctx.pool)
        rev_map = {}
        history = fs.node_history( resource_ctx.fsroot, self.svn_path, pool)
        count = 0
        try:
            while history:
                history = fs.history_prev( history, cross_copies, pool )
                if history is None: break
                path, rev = fs.history_location( history, pool )
                rev_map[ rev ] = path
                if limit and count >= limit:
                    break
                if (stop_after_revision and stop_after_revision > rev):
                    break
                count += 1
        finally:
            core.svn_pool_clear( pool )
            core.svn_pool_destroy( pool )
            
        return rev_map
        
    def getRevisionCreated(self):
        """
        return the revision that this node was created.
        """
        svn_ctx = self.getSVNContext()
        resource_ctx = svn_ctx.getResourceContext()

        pool = core.svn_pool_create(resource_ctx.pool)
        try:
            revision = fs.node_created_rev(resource_ctx.fsroot,
                                           self.svn_path,
                                           pool)
        finally:
            core.svn_pool_destroy(pool)

        return revision

    revision_created = property( getRevisionCreated, doc=getRevisionCreated.__doc__ )
    
    def isBinary(self):
        """
        does the node represent binary content 
        """
        mime_type = self.getProperty(core.SVN_PROP_MIME_TYPE)
        if mime_type is None:
            return 0        
        return core.svn_mime_type_is_binary(mime_type)

    binary = property( isBinary, doc=isBinary.__doc__ )
        
    def _modified( self ):
        # register ourselves with the data manager
        ctx = self.getSVNContext()
        resource_ctx = ctx.getResourceContext()
        dm = resource_ctx.getDataManager()
        dm.register( self )

