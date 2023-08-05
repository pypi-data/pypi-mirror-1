### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteConnectorBase class for the Zope 3 based remotefs package

$Id: remoteconnector.py 49266 2008-01-08 12:34:56Z cray $
"""
 
from zope.interface import Interface,implements
from interfaces import IRemoteConnector
from persistent import Persistent
from zope.app.container.contained import Contained

class RemoteConnectorBase(Contained,Persistent) :
    implements(IRemoteConnector)

    prefix = ""

    realm = ""

    username = ""
    
    def getp(self) :
        return self._password
    
    def setp(self,value) :
        if value :
            self._password = value    
        
    _password = ""

    password = property(getp,setp)

    def update(self,prefix,path) :
        return None                    
