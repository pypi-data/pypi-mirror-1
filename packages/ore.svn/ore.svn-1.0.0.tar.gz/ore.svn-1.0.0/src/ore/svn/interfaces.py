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
$Id: interfaces.py 1544 2006-08-15 00:56:07Z hazmat $
"""

## from zope import schema
from zope.interface import Interface
## from zope.app.location import ILocation
## from zope.app.filerepresentation.interfaces import IReadFile, IWriteFile
## from zope.app.container.interfaces import IReadContainer

#################################
# Exceptions

class InvalidRepositoryPath(Exception): pass
class RootPathViolation(Exception): pass
class UnsupportedNodeType(Exception): pass

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

## class ILogCollection( IReadContainer ):
##     """
##     a collection of log items
##     """


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

## class ISubversionReadContainer( IReadContainer, ISubversionNode ):
##     pass


## class ISubversionRepository( ISubversionReadContainer ):
##     pass

##     repository_path = schema.ASCIILine( title=u"repository_path", description=u"Path to a Repository")

##     svn_path = schema.ASCIILine( title=u"svn_path", description=u"Root Path Within a Repository")



    

    
