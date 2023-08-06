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
$Id: log.py 2205 2008-05-07 19:44:27Z hazmat $
"""

from logging import getLogger
from interfaces import DEBUG

from pprint import pprint
from svn import fs, core
from utils import make_time, format_date

#################################
# log class

__log = getLogger("ore.svn")

class _log:

    def debug(self, msg, extra='', **kwargs):
        if not DEBUG:
            return
        print msg
        __log( msg )

log = _log()


class SubversionLogEntry(object):

    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, **args):
        self.__dict__.update(args)

    def __repr__(self):
        return "<Log: %s>"%' '.join( self.__dict__.keys() )

    def beautifiedAge(self):
        if not self.__dict__.has_key('date'):
            return ''
        return format_date( self.date )

    def pprint(self):
        pprint( self.__dict__ )


#################################
# factories        

def SVNLogFactory(fsptr, revision, pool):
    
    author  = fs.revision_prop(fsptr, revision, core.SVN_PROP_REVISION_AUTHOR, pool)
    message = fs.revision_prop(fsptr, revision, core.SVN_PROP_REVISION_LOG, pool) or ''
    date    = fs.revision_prop(fsptr, revision, core.SVN_PROP_REVISION_DATE, pool)
    
    date = core.svn_time_from_cstring(date, pool)

    return SubversionLogEntry(author = author,
                              message = message,
                              date = make_time(date),
                              revision = revision
                              )

class SVNLogCollection:

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self):
        self.logs = []

    def addLog(self, paths, revision, author, date, message, pool):
        """
        Used for log gather callbacks
        
        notes in svn_repos.h, svn_types.h, svn_clients.h 
        
        typedef svn_error_t *(*svn_log_message_receiver_t)
        (void *baton,
        apr_hash_t *changed_paths,
        svn_revnum_t revision,
        const char *author,
        const char *date,  /* use svn_time_from_string() if need apr_time_t */
        const char *message,
        apr_pool_t *pool);
        """
        
        date = core.svn_time_from_cstring(date, pool)
        self.logs.append( SubversionLogEntry(author = author,
                                             message = message,
                                             date = make_time(date),
                                             revision = revision,
                                             paths = paths
                                             )
                          )

    def __getitem__(self, i):
        return self.logs[i]
    

    def getLogs(self):
        return self.logs


