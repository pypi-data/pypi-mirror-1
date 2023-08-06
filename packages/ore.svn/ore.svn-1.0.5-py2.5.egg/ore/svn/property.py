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

Property Mapping for nodes.
Node Propertysheets
Canonical Subversion PropertySheet

$Id: property.py 2205 2008-05-07 19:44:27Z hazmat $
"""

from cPickle import loads, dumps
from base64 import encodestring, decodestring

from svn import core
from zope.interface import implements
from interfaces import ISubversionProperties

class PropertyMapping( object ):
    """
    a dictionary like api to a node's properties that supports mutation
    to allow for usage like.

    node.properties['svn:mime-type'] = 'text/plain'
    node.properties['svn:externals'] = 'ore.svn https://svn.objectrealms.net/svn/public/ore.svn/trunk'
    del node.properties['svn:ignore']
    """
    __slots__ = ('_node')
    
    def __init__( self, node ):
        self._node = node
        
    def keys(self):
        return self._node.getProperties().keys()

    def values( self ):
        return self._node.getProperties().values()

    def __contains__( self, key ):
        return self[ key ]
    
    def __getitem__(self, key):
        return self._node.getProperty( key )

    def __setitem__( self, key, value ):
        self._node.setProperty( key, value )

    def __delitem__( self, key ):
        self._node.delProperty( key )

class node_property( object ):

    def __init__(self,  propname ):
        self.propname = propname
    
    def __get__( self, propsheet, name ):
        return propsheet.node.getProperty( self.propname)

    def __set__( self, propsheet, value ):
        if not isinstance( value, (str, unicode)):
            raise ValueError("can only set string properties %s %r"%(self.propname, value))
        if isinstance( value, unicode):
            value = value.encode('utf-8')
        propsheet.node.setProperty( self.propname, value )

    def __delete__( self, propsheet, name ):
        propsheet.node.delProperty( self.propname )

class list_property( node_property ):
    """ property descriptor which marshalls string list values into a single
        encoded but human readable string.
    """
    def __get__(self, propsheet, name):
        value = super( list_property, self).__get__( propsheet, name )
        if value is None:
            return ()
        return value.split(",\r\n")

    def __set__(self, propsheet, value):
        assert isinstance( value, (list, tuple) )
        value = ",\r\n".join( value ) 
        if isinstance( value, unicode):
            value = value.encode('utf-8')
        super( list_property, self ).__set__( propsheet, value )
        

class object_property( node_property ):
    """ node property using base64 encoded pickled strings.
    needs careful use, as a malcious client could set arbitrary
    values for a pickle.
    """
    def __get__(self, propsheet, name ):
        value = super( object_property, self ).__get__( propsheet, name )
        if value is None:
            return None
        assert isinstance( value, str )
        return loads( decodestring(value) )
    def __set__(self, propsheet, value):
        super( object_property, self).__set__(
            propsheet, encodestring( dumps( value ) ) )

class txn_property( object ):

    def __init__(self, propname ):
        self.propname = propname

    def __get__( self, txn, name ):
        return txn.dm.getProperty( self.propname )

    def __set__( self, txn, value ):
        return txn.dm.setProperty( self.propname, value )

    def __delete__( self, txn, name ):
        return txn.dm.delProperty( self.propname )
     

class NodePropertySheet( object ):
    """ property sheets are adapters for a node that allow attribute access
    to a specified set of properties.
    """
    __slots__ = ('node',)
    
    def __init__(self, node ):
        self.node = node

    def setup( cls, attr_prop_mapping, list_prop_mapping=None ):
        for attr_name, prop_name in attr_prop_mapping.items():
            setattr( cls, attr_name, node_property( prop_name ) )

        if not list_prop_mapping:
            return
        
        for attr_name, prop_name in list_prop_mapping.items():
            setattr( cls, attr_name, list_property( prop_name ) )

    setup = classmethod( setup )

    def setup2( cls, mapping ):
        attr_types = {'node':node_property,
                      'list':list_property,
                      'object':object_property }
        
        for attr_name, ( attr_type, prop_name ) in mapping.items():
            prop = attr_types[ attr_type ]( prop_name )
            setattr( cls, attr_name, prop )
            
    setup2 = classmethod( setup2 )
        
    
class SubversionProperties( NodePropertySheet ):
    """ Property sheet for the canonical subversion properties on a node
    """
    implements( ISubversionProperties )

def _wireSubversionProps( ):
    # these are the ones relevant for node usage.
    prop_listing = map( lambda x: x.strip(), """
    SVN_PROP_EOL_STYLE
    SVN_PROP_EXECUTABLE
    SVN_PROP_EXECUTABLE_VALUE
    SVN_PROP_EXTERNALS
    SVN_PROP_IGNORE
    SVN_PROP_KEYWORDS
    SVN_PROP_MIME_TYPE
    """.split() )

    prop_map = {}

    for p in prop_listing:
        prop_name = getattr( core, p )
        attr_name = prop_name.rsplit(':',1)[-1].replace('-', '_')
        prop_map[ attr_name ] = prop_name

    SubversionProperties.setup( prop_map )

_wireSubversionProps()    
    
                        
    

