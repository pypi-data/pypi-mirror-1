### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteConnectorBase class for the Zope 3 based ng.app.remotefs package

$Id: remoteconnectorsvn.py 49290 2008-01-08 16:51:54Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49290 $"

from zope.interface import Interface
from remoteconnector import RemoteConnectorBase
import urllib2
from urllib import quote
from ng.app.remotefs.remoteupdate.remoteupdate import RemoteUpdateBase
from ng.content.remotearticle.remotearticle.remotearticle import RemoteArticle
import svntest
from ng.app.remotefs.remotefile.remotefile import RemoteFile
from ng.app.remotefs.remotecontainer.remotecontainer import RemoteContainer
from zope.cachedescriptors.property import Lazy

import re

mm = re.compile(".*\.(txt|doc|py)$")

from ng.app.remotefs.exceptions import RemoteFSInvalidObject
from svn.core import SubversionException

class RemoteConnectorSVN(RemoteUpdateBase, RemoteConnectorBase) :

    def url(self,prefix,path) :
        # TODO: Похоже эта проверка мешает
        #if prefix != self.prefix :
        #    raise ValueError,"Invalid prefix %s instead %s" % (prefix,self.prefix)

        return self.prefix+quote(str(path))

    def date(self,prefix,path) :
        try :
            return self._v_svn.date(self.url(prefix,path))
        except SubversionException,msg :
            raise RemoteFSInvalidObject,msg

    def update(self,prefix,path) :
        url = self.url(prefix,path)
        s = self._v_svn.cat(url)
        try :
            return s.decode("utf-8")
        except :
            return s


    def list(self,prefix,path) :
        url = self.url(prefix,path)
        if svntest.isdir(self._v_svn.info(url)) :
            for item, v in self._v_svn.list(url).iteritems():
                if svntest.isdir(v) :
                    factory = RemoteContainer
                else :
                    if mm.match(item) :
                        factory = RemoteArticle
                    else:
                        factory = RemoteFile
                yield item,factory
        else :
            raise ValueError,"Node is terminal: %s" % url

    @Lazy
    def _v_svn(self):
        return svntest.SvnClient()
