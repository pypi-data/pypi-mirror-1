### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteUpdateBase class for the Zope 3 based ng.app.remotefs package

$Id: remoteupdate.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"
 
from zope.interface import Interface,implements
from interfaces import IRemoteUpdate
from zope.proxy import removeAllProxies
from zope.app.zapi import getUtilitiesFor
from zope.app.catalog.interfaces import ICatalogQuery
from ng.app.remotefs.remoteconnector.interfaces import IRemoteConnector
from ng.app.remotefs.exceptions import RemoteFSInvalidObject
from transaction import get


def f(x,y) :
    if x.date is None :
        return -1
    elif y.date is None :
        return 1
    else :
        return cmp(x.date,y.date)        
                    

class RemoteUpdateBase(object) :
    implements(IRemoteUpdate)    

    def __init__(self,*kv,**kw) :
        super(RemoteUpdateBase,self).__init__(*kv,**kw)

    def update_list(self,update="") :
        return self.update_list_urls(
                 update and [ y for y in [ x.strip() for x in update.split("\n")] if y ] or []
                 )
    
    def update_list_urls(self,urls) :
        prefix = IRemoteConnector(self).prefix
        catalogs = list(getUtilitiesFor(ICatalogQuery, self))
        already = set()

        if urls :
            paths = [y[len(prefix):].strip() for y in urls if prefix == y[0:len(prefix)] ] 

            for path in paths :
                print "The path",path,"running..."
                number = 0
                for name,catalog in catalogs :
                    for rf in catalog.searchResults(prefix=(prefix,prefix),path=(path,path)) :
                        rf.update(already)
                        get().commit()
                        number += 1
                print "The",number,"objects has been updated"                        
        else :
            for name,catalog in catalogs :
                for rf in sorted(catalog.searchResults(prefix=(prefix,prefix)),f) :
                    print "The url",prefix+rf.path,"update begun",rf.date
                    try :
                        rf.update(already)
                    except RemoteFSInvalidObject,msg :
                        print "The url",prefix+rf.path,"update failed becouse of",msg
                    else :
                        print "The url",prefix+rf.path,"update complite"
                        get().commit()
