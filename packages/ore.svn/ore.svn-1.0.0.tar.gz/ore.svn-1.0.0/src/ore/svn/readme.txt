-------
ore.svn
-------

Offers an alternative pythonic r/w api to subversion that utilizes the underlying libsvn api,
and does automatic memory management svn (1.0-1.3), and transaction handling. the major
design goal is to make working  with subversion from python fun and easy.

it operates directly on the subversion repository layer, and needs direct filesystem access
to the repository.

ore.svn is licensed under the LGPL

API
---


SubversionContext 
=================
  
represents access to a node hierarchy within a subversion repository. 
   
  >> from ore.svn import SubversionContext
  >> ctx = SubversionContext('tests/myrepo') 
   
you can also limit operations it to a particular path within a repository.
which will bind the context to a particular subtree.

  >> ctx = SubversionContext('test/myrepo', '/myproject')   

to access the svn nodes from the context, we access the root of
the node tree on the context.

  >> node = ctx.root

the path of any node witin the repository is represented by the svn_path attribute.
  >> node.svn_path
  '/myproject'

file access

using repository commit hooks for transactions

using authz

pickle safe
 
SubversionNode 
==============

represents a file or directory within a subversion repository, provides generic property
handling and revision history introspection.

repository revision properties on nodes are accessible via attributes

the last log message of the revision the node was last modiied.

  >> node.last_log # information from the last 

the date the node was last modified

  >> node.modification_time

the revision the node was created

  >> node.revision_created

the node's container node

  >> node.parent_node

custom node properties are accessible via a mutable properties mapping object

  >> node.properties['svn:externals'] = "ore.svn https://svn.objectrealms.net/svn/public/ore.svn"

all nodes have an api for discovering their path ancestry with the corresponding
revision information.  

 >> file = node['myfile.txt']
 >> log_entries = file.getMappedLogEntries()
 >> for entry in log_entries:
        print "Revision and Path", entry.revision, entry.rev_path 

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
  None

copy a node with the given copy name

  >> copied_file = directory.copy( "zebra", file )

to create a directory

  >> subdirectory = directory.makeDirectory("baz")
  >> newfile = subdirectory.makeFile("zebra.txt")
 
moving a node

  >> directory['horses.txt'] = newfile
  >> 'zebra.txt' in subdirectory
  False

to delete nodes the standard mapping api works

  >> del directory['baz']
  >> del directory['horses.txt']

SubversionFile
==============

in addition to the svnnode log inspection, files offer some basic diff methods

  >> file.contents

replace the file contents with a string

  >> file.write("hello world")

size of the file's contents

  >> file.size

the md5 checksum of the content

  >> file.checksum

the mime type of the 

  >> file.mime_type

Location and History
 

Streaming
 
to stream the contents of a file, provide a stream to the getContents api

  >> stream = os.tmpfile()
  >> file.getContents( writer=stream )

to write a stream's contents to the file use the writeStream

 >> fh = open('bigfile.pdf')
 >> file.writeStream( fh )

Transactions
============
 
ore.svn integrates with zope's transaction api for transaction management. transaction
handling is automatic, any modification of a node, automatically creates a corresponding
subversion transaction. the system does not employ subversion's delta editor api, the nodes
are modified in place.

 >> import transaction

 >> transaction.abort() # abort all the modifications we've made so far

 >> root.makeDirectory("reptiles")
 >> del root['oldproject']
 >> transaction.commit() # commit our changes

there is an alternative api for those who prefer, which also exposes setting revision
properties.

 >> root.makeDirectory("mammals")
 <SubversionDirectory mammals>

 >> svntxn = ctx.transaction

 >> svntxn.author = "kapil"
 >> svntxn.message = "made directory for mammals"

 >> svntxn.commit()

if an access name is set then the author is set on transaction creation to the access name.

Locking
=======

The svn locking api, requires setting a username for filesystem access, as locks have associated
owners. Locks currently are only applicable on files.

 >> ctx.setAccess("zookeeper")
 >> file_node = root['horses.txt']

Tree Iterators
==============

 provide a quick way to iterate and operate on a subversion directory tree.

 >> from ore.svn.tree import fileIterator, directoryIterator, lockTree, unlockTree
 
 print all the path to files in the directory and its children
 >> for file_node in fileIterator( root ):
       print file_node.path

 lock and unlock all the files in the directory and its subdirectories (tree)
 >> lockTree( directory )
 >> unlockTree( directory )

PropertySheets
==============

?? options affecting behavior.. repository commit vs. fs commit

Examples
--------

Setting Files Properties
========================

basic usage... a script to ensure all non binary files have svn:keywords set.

  >> import transaction
  >> from ore.svn import SubversionContext, fileIterator
  >> from ore.svn.tree import fileIterator
 
open a subversion context against the root of the svn repository

  >> ctx = SubversionContext('/var/lib/svn/repos')

get the root directory, supports the dictionary protocol
  >> root = ctx.root

iterate through all files in the tree, and tag the rest
 >> for file_node in fileIterator( root ):
      if file_node.binary:
           continue
      if not 'svn:keywords' in node.properties:
           node.properties['svn:keywords'] = "Id"

 commit our changes
 >> transaction.commit()

Find Changed Tags
=================

find tags that have been modified after their creation.

 >> for tag in ctx['myproject']['tags'].directories:
    	logs = tag.getLogEntries( changed_paths=True, strict_history=True  )
	# if the only revision is the tag creation, then it hasn't been modified
        if len(logs) == 1: 
            continue
	  
	for log in logs[1:]:
		print "Tag Modified After Creation - by %s on %s in rev %s"%( log.author, log.date, log.revision)		

installation
------------

 $ easy_install ore.svn

 the library features some basic integration with zope3 for interface declarations
 and transactions and has dependencies on those libraries.


todo
----

 - use repos get file revs for file.getAnnotatedLines
 - options for respect authz
 - options for using repo commit hooks, property change hooks
 - stream api for files
  
