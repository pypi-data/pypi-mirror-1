### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteRegistryBase class for the Zope 3 based remotefs package

$Id: remoteregistryitem.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"
 
from zope.interface import Interface,implements
from interfaces import IRemoteRegistryItemContained,IRemoteRegistryItem
from persistent import Persistent
from zope.app.container.contained import Contained
from persistent.list import PersistentList
from zope.size.interfaces import ISized

class RemoteRegistryItem(PersistentList,Contained) :
    implements(IRemoteRegistryItem,IRemoteRegistryItemContained,ISized)

    path = ""
    
    @property
    def title(self) :
        return self.path
    
    # ========================= ISized ============================
    def sizeForDisplay(self):
        s = u"%d objects" % len(self)
        return s
                        
    def sizeForSorting(self):
        return len(self)
                                          
    