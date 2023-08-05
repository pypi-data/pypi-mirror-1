### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteObjectBase class for the Zope 3 based ng.app.remotefs package

$Id: remoteobject.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

from zope.interface import Interface, implements
from zope.app.zapi import  getUtilitiesFor
import datetime
from interfaces import IRemoteObject
from ng.app.remotefs.remoteconnector.interfaces import IRemoteConnector
from zope.app.zapi import getUtility, getUtilitiesFor

class RemoteObjectBase(object) :
    implements(IRemoteObject)

    prefix = ""

    _path = ""

    date = None

    def getpath(self) :
        return self._path
        
    def setpath(self,value) :
        for name, utility in getUtilitiesFor(IRemoteConnector,context=self) :
            if value[0:len(name)] == name :
                self._path = value[len(name):]
                self.prefix = name
                break
        else :                
            self._path = value
            
        if not self.title :
            items = self._path.split("/")
            items.reverse()

            for item in items :
                if item :
                    self.title = item
                    break
        
    path = property(getpath,setpath)

    def check_update(self) :
        return  self.date is None or getUtility(IRemoteConnector,self.prefix,context=self).date(self.prefix,self.path) > self.date 
            
    def update(self) :
        self.date = datetime.datetime.today()
                    
                