### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteRegistryBase class for the Zope 3 based ng.app.remotefs package

$Id: remoteregistry.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"
 
from zope.interface import Interface,implements
from interfaces import IRemoteRegistryContainer,IRemoteRegistry
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.app.container.btree import BTreeContainer
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOSet,OOBTree
from remoteregistryitem import RemoteRegistryItem
from zope.proxy import removeAllProxies

class RemoteRegistryBase(BTreeContainer) :
    implements(IRemoteRegistryContainer,IRemoteRegistry)    

    num = 0     
    def __init__(self,*kv,**kw) :
        super(RemoteRegistryBase,self).__init__(*kv,**kw)
        self.registry = OOBTree()
    
    def update_all(self,update) :
        
        for path in set([y for y in [ x.strip() for x in update.split("\n")] if y ]) \
                   .intersection(self.registry) :
            self.registry[path].update()
        
    def add_registry(self,ob) :
        try :
            items = self.registry[ob.path]
        except KeyError :
            self.num = self.num + 1
            key = "%016u" % self.num
            items = self[key] = self.registry[ob.path] = RemoteRegistryItem()
   
        items.append(removeAllProxies(ob))

    

    def del_registry(self,ob) :
        try :
            items = self.registry[ob.path]
        except KeyError :
            pass
   
        items.remove(ob)
        if not len (items) :
            del(self[items.__name__])
        
        
            