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
Repository utilities functions for creation, copying, and deleting.

$Id: repos.py 2205 2008-05-07 19:44:27Z hazmat $
"""

import os
from os import path
from context import SubversionContext
from svn import fs, core, repos

def _path_check( repo_path, create=False ):
    repo_path = path.abspath( path.expanduser( path.expandvars( repo_path ) ) )

    if repo_path.endswith('/'):
        repo_path = repo_path[:-1]
        
    if create and path.exists( repo_path ):
        raise RuntimeError("%s already exists"%repo_path)
    elif not create and not path.exists( repo_path ):
        raise RuntimeError("%s path does not exist"%repo_path)

    if create and not path.exists( path.dirname( repo_path ) ):
        raise RuntimeError("parent path does not exist %s"%repo_path )

    _mp = repo_path
    if create: # acccess check the parent
        _mp = path.dirname( repo_path )

    access_checks = (os.R_OK, os.W_OK, os.X_OK)
    for ac in access_checks:
        if not os.access( _mp, ac ):
            raise RuntimeError("Insufficient Privileges to %s %s"%(_mp, ac))
        
    return repo_path

def create( repo_path, repo_type=fs.SVN_FS_TYPE_FSFS, noreturn=False ):
    """
    create a repository at the given path with the given repository type
    """

    repo_path = _path_check( repo_path, create=True )

    if not repo_type in [ fs.SVN_FS_TYPE_FSFS, fs.SVN_FS_TYPE_BDB ]:
        raise RuntimeError("invalid repository type - %s"%repo_type )
    
    pool = core.svn_pool_create( None)
    try:
        config = { fs.SVN_FS_CONFIG_FS_TYPE : repo_type }
        reposptr = repos.create( repo_path, None, None, None, config, pool )
    finally:
        core.svn_pool_clear( pool )
        core.svn_pool_destroy( pool )

    if noreturn:
        return

    return SubversionContext( repo_path )

def copy( src_repo_path, target_repo_path ):
    """ copy a repository from the src path to the target path """
    src_repo_path = _path_check( src_repo_path )
    target_repo_path = _path_check( target_repo_path, create=True )
    
    pool = core.svn_pool_create( None)        
    try:
        repo_type = fs.type( src_repo_path, pool )
        reposptr = repos.hotcopy( src_repo_path, target_repo_path, 0, pool )
    finally:
        core.svn_pool_clear( pool )
        core.svn_pool_destroy( pool )

    return SubversionContext( target_repo_path )

def destroy( repo_path ):
    """ destroy the repository at the given path """
    repo_path = _path_check( repo_path )
    pool = core.svn_pool_create( None)
    try:
        reposptr = repos.delete( repo_path, pool )
    finally:
        core.svn_pool_clear( pool )
        core.svn_pool_destroy( pool )

def transactions( repo_path ):
    " list open transaction names in the given repository path "
    ctx = SubversionContext( repo_path )
    return fs.list_transactions( ctx.getResourceContext().fsptr, ctx.pool )
    
    



    
    

    

