### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteObject class for the Zope 3 based remotefs package

$Id: remoteobject.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"
 
from zope.interface import Interface, implements
from zope.app.zapi import  getUtilitiesFor
import datetime
from interfaces import IRemoteObject,IRemoteStat
from ng.app.remotefs.remoteconnector.interfaces import IRemoteConnector
from zope.app.zapi import getUtility, getUtilitiesFor
import datetime 

class RemoteObjectBase(object) :
    implements(IRemoteObject,IRemoteStat)

    prefix = ""

    _path = ""

    date = None

    @property
    def last_update(self) :
        return self.date

    title = ""

    length = 0
    
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
        print getUtility(IRemoteConnector,self.prefix,context=self).date(self.prefix,self.path)
        print self.date
        print datetime.datetime.now()
        if self.date is None :
            print "This is new file, will be updated"
            return True
        elif datetime.datetime.now() - self.date < datetime.timedelta(0,3600) :
            print "This file updated recently, skiped"
        elif getUtility(IRemoteConnector,self.prefix,context=self).date(self.prefix,self.path) > self.date :
            print "There is newest original of this file, updated"
            return True
                    
        print "Updating is not interesting"                        
            
    def update(self,already=set()) :
        self.date = datetime.datetime.today()
                    
                