### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteFile class for the Zope 3 based remotefs package

$Id: remotefile.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"
 
from zope.interface import Interface, implements
from persistent import Persistent

from ng.app.remotefs.interfaces import IRemoteObject
from ng.app.remotefs.remoteconnector.interfaces import IRemoteConnector
from interfaces import IRemoteFile
from zope.app.zapi import getUtility, getUtilitiesFor
from zope.app.container.contained import Contained
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent import Attributes

import datetime

from ng.app.remotefs.remoteobject import RemoteObjectBase
from transaction import get

class RemoteFile(RemoteObjectBase,Persistent,Contained) :
    implements(IRemoteFile)

    title = ""

    body = ""
    
    date = None

    @property
    def length(self) :
        return len(self.body)

    def update(self,already=set()) :
        if (self.prefix,self.path) not in already :
            res = self.check_update() 
            print "Result",res
            if res :
                print self.__name__
                for i in range(1,10) :
                    print "Try update ...",i
                    try :
                        self.body = getUtility(IRemoteConnector,self.prefix,context=self).update(self.prefix,self.path)
                    except Exception,msg :
                        print "Fault",msg
                    else :
                        break
                else :
                    return                                                                        
                                    
                super(RemoteFile,self).update(already)
                notify(ObjectModifiedEvent(self, Attributes(IRemoteFile,["body","date"])))
                get().commit()
            already.add((self.prefix,self.path))                
