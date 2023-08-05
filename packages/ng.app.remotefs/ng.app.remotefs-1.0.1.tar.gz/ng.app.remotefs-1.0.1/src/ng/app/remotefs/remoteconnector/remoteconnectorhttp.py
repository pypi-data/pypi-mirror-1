### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteConnectorBase class for the Zope 3 based ng.app.remotefs package

$Id: remoteconnectorhttp.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

from zope.interface import Interface
from remoteconnector import RemoteConnectorBase
import urllib2
from urllib import quote
import re
from ng.app.remotefs.remoteupdate.remoteupdate import RemoteUpdateBase
from chardet import detect
import datetime
                
match = re.compile("^text/.*;\s+charset=(?P<enc>.*)$").match                
class RemoteConnectorHTTP(RemoteUpdateBase, RemoteConnectorBase) :
    
    def update(self,prefix,path) :
        if prefix != self.prefix :
            raise ValueErroe,"Invalid prefix %s instead %s" % (prefix,self.prefix)

        url = self.prefix+quote(path)
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(self.realm, url, self.username, self.password)
        opener = urllib2.build_opener(auth_handler)
        o=opener.open(url)
        try :
            enc=match(o.info()['content-type']).groupdict()['enc']
        except (KeyError,AttributeError) :
            res = o.read()
            return  res.decode(detect(res)['encoding'])
        else :
            return o.read().decode(enc)

    def date(self,prefix,url) :
        return datetime.datetime.today()
        