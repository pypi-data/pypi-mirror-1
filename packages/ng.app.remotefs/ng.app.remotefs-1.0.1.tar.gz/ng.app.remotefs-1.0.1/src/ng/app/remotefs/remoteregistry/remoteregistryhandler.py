### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of functions used to dispatch events to 
cache storage.

$Id: remoteregistryhandler.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Anton Oprya,2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

from zope.app import zapi
from interfaces import IRemoteRegistry
from zope.component import ComponentLookupError
from zope.proxy import removeAllProxies

def addHandler(ob,event) :
    try :
        zapi.getUtility(IRemoteRegistry, ob.prefix, context=ob).add_registry(ob)
    except ComponentLookupError,msg :
        print "ComponentLookupError",msg

def modifyHandler(ob,event) :
    ob = removeAllProxies(ob)    

        

def delHandler(ob,event) :
    try :
        zapi.getUtility(IRemoteRegistry, ob.prefix, context=ob).del_registry(ob)
    except ComponentLookupError,msg :
        print "ComponentLookupError",msg
        
