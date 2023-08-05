### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteContainer class for the Zope 3 based ng.app.remotefs package

$Id: remotecontainer.py 49360 2008-01-11 21:18:17Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49360 $"

from zope.interface import Interface,implements
from zope.app.container.contained import Contained
from zope.app.container.btree import BTreeContainer
from interfaces import IRemoteContainer,IRemoteContainerContent
from interfaces import IRemoteDescriptor,IRemoteDescriptorContainer
from ng.app.remotefs.interfaces import IRemoteObject
from ng.app.remotefs.remoteconnector.interfaces import IRemoteConnector
from ng.app.remotefs.remoteobject import RemoteObjectBase
from zope.app.zapi import getUtility, getUtilitiesFor
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectCreatedEvent
from zope.event import notify
import datetime 
from transaction import get 

class RemoteDescriptorContainer(BTreeContainer,Contained) :
    implements(IRemoteDescriptorContainer)

class RemoteDescriptor(Contained) :
    implements(IRemoteDescriptor)
    
    isordinal = False
    isdeleted = False 
    
    def __init__(self,isordinal=True, isdeleted=False) :
        super(RemoteDescriptor,self).__init__()
        self.isordinal = isordinal
        self.isdeleted = isdeleted


class RemoteContainer(RemoteObjectBase, BTreeContainer, Contained) :
    implements(IRemoteContainer,IRemoteObject,IRemoteContainerContent)
    descriptors = None    

    def __init__(self,*kv,**kw) :
        super(RemoteContainer,self).__init__(*kv,**kw)
        self.descriptors = RemoteDescriptorContainer()
        self.descriptors.__parent__= self
        self.descriptors.__name__ = "descriptors"
        
    def __setitem__(self,name,ob) :
        super(RemoteContainer,self).__setitem__(name,ob)
        self.descriptors[name] = RemoteDescriptor()        
        self.descriptors[name].__parent__ = self.descriptors
        self.descriptors[name].__name__ = name
        
    def __delitem__(self,name) :
        super(RemoteContainer,self).__delitem__(name)        
        try :
            if self.descriptors[name].isordinal :
                del(self.descriptors[name])
            else :            
                self.descriptors[name].isdeleted = True
        except KeyError,msg:
            print "Warning:",msg,"during delete"                
            
    def clearordinal(self,name) :
        self.descriptors[name].isordinal = False

    def update(self,already=set()) :
        if (self.prefix,self.path) not in already :
            if self.check_update() :
                super(RemoteContainer,self).update(already)

            self.length = 0
            for (name,factory) in getUtility(IRemoteConnector,self.prefix,context=self).list(self.prefix,self.path) :
            
                try :
                    descriptor = self.descriptors[name]
                except KeyError :
                    self[name] = node = factory()
                    node.prefix = self.prefix
                    node._path = self._path + "/" + name
                    print "Node %s created" % name
                    notify(ObjectCreatedEvent(node))
                    notify(ObjectModifiedEvent(node, Attributes(IRemoteObject,["prefix","_path"])))
                    self.clearordinal(name)
                else :
                    print "Node %s already exsist (ordinal=%s,deleted=%s) " % (name,descriptor.isordinal,descriptor.isdeleted)
                    continue
                    if not descriptor.isordinal and not descriptor.isdeleted :
                        try :
                            node = self[name]
                        except KeyError :
                            # FIXME! It's temporal solution some common problem
                            del self.descriptors[name]
                            continue
                            
                    else :
                        print "Continue"
                        # FIXME!! continue
            
                print "Node %s update has now begun" % name
                node.update(already)                
                self.length+=node.length
                print "Node %s updated complete" % (node.prefix+node._path)
                get().commit()
        already.add((self.prefix,self.path))        