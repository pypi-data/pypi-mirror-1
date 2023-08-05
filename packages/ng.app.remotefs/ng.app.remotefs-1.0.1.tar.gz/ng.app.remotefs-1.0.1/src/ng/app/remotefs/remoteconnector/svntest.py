### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Wrapper arround SVN

$Id: svntest.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Anatoly Zaretsky, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"
 
import svn.core
import svn.client

import cStringIO
import datetime


class IsDirectoryError(ValueError):
    pass


def isdir(entry):
    return entry.kind == svn.core.svn_node_dir

class SvnClient(object):

    def __init__(self):
        rev = svn.core.svn_opt_revision_t()
        rev.kind = svn.core.svn_opt_revision_head
        self._rev = rev


    def init_pool(self) :
        pool = svn.core.Pool()
        ctx = svn.client.create_context(pool)
        ctx.auth_baton = svn.core.svn_auth_open(
          [ svn.core.svn_auth_get_simple_provider(pool)
          , svn.core.svn_auth_get_username_provider(pool)
          , svn.core.svn_auth_get_ssl_server_trust_file_provider(pool)
          , svn.core.svn_auth_get_ssl_client_cert_file_provider(pool)
          , svn.core.svn_auth_get_ssl_client_cert_pw_file_provider(pool)
          ]
          , pool)
        return pool,ctx

    def _fix_path(self, url, pool):
        return svn.core.svn_path_canonicalize(url, pool)

    def date(self, url):
        return datetime.datetime.fromtimestamp(self.info(url).last_changed_date/1000000.0)

    def info(self, url):
        res = []
        def receiver(path, raw_data, pool):
            res.append(raw_data)
        pool,ctx = self.init_pool()            
        svn.client.info(self._fix_path(url,pool), self._rev, self._rev, receiver, False, ctx, pool)
        pool.destroy()
        assert len(res) == 1
        return res[0]

    def list(self, url, recursive=False):
        pool,ctx = self.init_pool()
        res = svn.client.ls(self._fix_path(url,pool), self._rev, recursive, ctx, pool)
        pool.destroy()
        return res

    def cat(self, url):
        try :
            pool,ctx = self.init_pool()    
            try:
                s = cStringIO.StringIO()
                svn.client.cat(s, self._fix_path(url,pool), self._rev, ctx, pool)
                return s.getvalue()
            except svn.core.SubversionException, e:
                if e.apr_err == svn.core.SVN_ERR_CLIENT_IS_DIRECTORY:
                    raise IsDirectoryError(e[0])
                else:
                    raise
        finally :
            print 'destroy in cat'
            pool.destroy()
            
            
_single_call = lambda class_, method: lambda *kv, **kw: getattr(class_(), method)(*kv, **kw)

info = _single_call(SvnClient, 'info')
list = _single_call(SvnClient, 'list')
cat = _single_call(SvnClient, 'cat')

# info_attrs = ['URL', 'rev', 'kind', 'repos_root_URL',
#               'repos_UUID', 'last_changed_rev',
#               'last_changed_date', 'last_changed_author']
#
# dirent_attrs = ['kind', 'size', 'has_props', 'created_rev', 'time', 'last_author]
#
# svn_node_kind_t:
#   svn.core.svn_node_none
#   svn.core.svn_node_file
#   svn.core.svn_node_dir
#   svn.core.svn_node_unknown

