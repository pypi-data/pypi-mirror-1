-------
ore.svn
-------

Offers an alternative pythonic r/w api to subversion that utilizes the underlying libsvn api,
and does automatic memory management svn (1.0-1.5), and transaction handling. the major
design goal is to make working with subversion from python fun and easy. Its been in use
and around since 2002 (svn 0.1x series).

it operates directly on the subversion repository layer, and needs direct filesystem access
to the repository.

ore.svn is licensed under the Apache Public License (2.0)

Installation
------------

To install the package, you must have the python subversion bindings installed. Although ore.svn
supports older versions of subversion, the recommended version is the latest release, as they
all have bug fixes and improvements for the language bindings. Once you have the bindings, to
install this package:

 $ easy_install ore.svn

the library features some basic integration with zope3 for interface declarations and transactions 
and has dependencies on those libraries (zope.interface, transaction) which will be installed
alongside it.

API
---

SubversionContext 
=================
  
represents access to a node hierarchy within a subversion repository:
   
  >>> from ore.svn import SubversionContext
  >>> ctx = SubversionContext( test_repo_path )
   
you can also limit operations it to a particular path within a repository.
which will bind the context to a particular subtree:

  >>> another_ctx = SubversionContext( test_repo_path, '/myproject')   

to access the svn nodes from the context, we access the root of
the node tree on the context:

  >>> node = ctx.root

the path of any node witin the repository is represented by the svn_path attribute.

  >>> node.svn_path
  '/'

 
SubversionNode 
==============

represents a file or directory within a subversion repository, provides generic property
handling and revision history introspection.

repository revision properties on nodes are accessible via attributes

the last log message of the revision the node was last modified:

  >>> node.last_log # information from the last 
  <Log: date message author revision>

the date the node was last modified:

  >>> node.modification_time
  datetime.datetime(2004, 3, 27, 18, 1, 4)

the revision the node was created:

  >>> node.revision_created
  5

the node's container node:

  >>> node.parent_node
  <ore.svn.directory.SubversionDirectory object at ...>

custom node properties are accessible via a mutable properties mapping object:

  >>> node.properties['svn:externals'] = "ore.svn https://svn.objectrealms.net/svn/public/ore.svn"

all nodes have an api for discovering their path ancestry with the corresponding
revision information:

  >>> file = node['core']['elephants.txt']
  >>> log_entries = file.getMappedLogEntries()
  >>> for entry in log_entries:
  ...    print "Revision and Path", entry.revision, entry.rev_path 
  Revision and Path 4 /core/elephants.txt
  Revision and Path 2 /core/elephants.txt
  Revision and Path 1 /core/elephants.txt

SubversionDirectory
===================

directories use the standard python mapping interface to expose their children:

  >>> directory = node # the root is also a directory, alias it for clarity
  >>> directory.keys()
  ['core']

We can also use the files and directories attributes to access just those types of child nodes.

  >>> directory.files
  []

Or see see if a file is contained in a directory by name

  >>> "readme.txt" in directory
  False

  >>> directory = directory['core']
  >>> directory.keys()
  ['elephants.txt', 'resources', 'cats.txt']

  >>> file = directory['cats.txt']
  >>> directory.get('nonexistant')

we copy a node in a directory with the given copy name. 

  >>> copied_file = directory.copy( "zebra.txt", file )

to create a directory, or empty file.

  >>> subdirectory = directory.makeDirectory("baz")
  >>> newfile = subdirectory.makeFile("bear.txt")
 
we can move a node, from a previous location to a new location via assignment into a
directory.

  >>> directory['horses.txt'] = directory['elephants.txt']
  >>> 'elephants.txt' in directory
  False

to delete nodes, the standard mapping api works

  >>> del directory['horses.txt']

SubversionFile
==============

in addition to standard node log inspection, files offer some additional methods, we can
introspect the content of a file via accessing the contents attribute.

  >>> file.contents
  'hello world\nrevision 2\n\n'

and write to the file replace the file contents with a string.

  >>> file.write("old cat new tricks")

alternatively we could just do assignment to the contents attribute.

  >>> file.contents = "abc"

for larger files, we can use a stream api to write the contents

  >>> from StringIO import StringIO
  >>> in_stream = StringIO("When angry, count ten, before you speak; if very angry, a hundred.")
  >>> file.writeStream( in_stream )

or to read them.

  >>> out_stream = StringIO()
  >>> file.read( writer=out_stream )
  >>> out_stream.getvalue()
  'When angry, count ten, before you speak; if very angry, a hundred.'

additional properties, size of the file's contents

  >>> file.size
  66L

the md5 checksum of the content

  >>> file.checksum
  '8c3b9a49408f09648a7b0494af5d88e5'

and its mime type.

  >>> file.mime_type
  'text/plain'

Location and History
++++++++++++++++++++

we can examine the history of any node using a myraid of api calls. getLog returns the log entry 
for a particular revision, the most recent by default.

  >>> file.getLog()
  <Log: date message author revision>

we can also get all the log entries for a node, by invoking getLogEntries.
 
  >>> for i in file.getLogEntries(): print i.date, i.author, i.message,
  2004-03-27 17:50:49 hazmat moving files
  2004-03-27 17:50:20 hazmat second commit
  2004-03-27 17:49:07 hazmat initial import

Streaming
+++++++++
 
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

  >>> from ore.svn.tree import fileIterator, lockTree, unlockTree
 
 print all the path to files in the directory and its children

  >>> ctx = SubversionContext( test_repo_path )


  >>> for file_node in fileIterator( ctx.root ):
  ...   print file_node.path

 lock and unlock all the files in the directory and its subdirectories (tree).

  >>> lockTree( ctx.root, 'lock-token-abc' )

 To unlock we need to pass in the same token, or force via the break_locks boolean keyword argument

  >>> unlockTree( ctx.root, 'lock-token-abc' )

PropertySheets
==============

todo - documentation


