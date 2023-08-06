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
$Id: interfaces.py 2205 2008-05-07 19:44:27Z hazmat $
"""
from zope.interface import Interface

#################################
# Exceptions

class InvalidRepositoryPath(Exception): pass
class RootPathViolation(Exception): pass
class UnsupportedNodeType(Exception): pass
class NoTransaction(Exception): pass

#################################
# Globals
DEBUG = 0
CHUNK_SIZE = 16384
_marker = object()
HEAD = 0

class ISubversionNode( Interface ):

    #node_id = schema.ASCIILine("node_id", "Subversion Node Id")


    def getModificationTime():
        """
        """

    def getProperty( property_name ):
        """
        """

    def getProperties():
        """
        """

    def getRevisionPathMap():
        """
        """

    def getRevisionCreated():
        """
        """

    def getMappedLogEntries():
        """
        """

    def getLog( revision=HEAD):
        """
        """


class ISubversionFile( ISubversionNode ):

    def isBinary():
        """
        """

    def getMimeType():
        """
        """

    def getContents( revision=None, writer=None):
        """
        """

    def getSize():
        """
        """

    def getAnnotatedLines( revision_set=(), include_copies=True):
        """
        """

    def lock():
        """
        lock the node
        """

    def unlock():
        """
        unlock the node
        """

class ISubversionDirectory( ISubversionNode ):
    """
    """

class ISubversionContext( Interface ):
    pass

class IPropertySheet( Interface ): pass
class ISubversionProperties( IPropertySheet ): pass

class ILogEntry( Interface ):
    pass

##     author = schema.ASCIILine( title=u"author", description=u"Author of the Revision")
##     message = schema.ASCIILine( title=u"message", description=u"Commit Message")
##     date = schema.Datetime( title=u"date", description=u"Date of the Revision")
##     revision = schema.Int( title=u"revision", description=u"Revision Number")
##     paths = schema.List( value_type=schema.ASCIILine(),
##                          required=False,
##                          unique=True)

class ILogFormatter( Interface ):

    def __call__( text ):
        """
        return text formatted
        """


    

    
