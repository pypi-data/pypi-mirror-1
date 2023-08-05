### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.remotefs package

$Id: interfaces.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Choice, Password
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.size.interfaces import ISized

from ng.app.remotefs.remoteupdate.interfaces import IRemoteUpdateForm, IRemoteUpdate

class IRemoteRegistryForm(IRemoteUpdateForm) :
    """ Interface to update remote files """

class IRemoteRegistry(IRemoteUpdate) :
    """ Interface to update remote files """

class IRemoteRegistryItemBase(IContained) :
    pass

class IRemoteRegistryContainer(IContainer) :
        def __setitem__(name, object):
            """Add a Registry Item object."""
        
        __setitem__.precondition = ItemTypePrecondition(IRemoteRegistryItemBase)

class IRemoteRegistryItemContained(IRemoteRegistryItemBase) :
    __parent__ = Field(
            constraint = ContainerTypesConstraint(IRemoteRegistryContainer))

class IRemoteRegistryItem(ISized) :
    """ Registry item about remote files """
    
    title = TextLine(title = u'Title',
        description = u'Title',
        default = u'',
        required = False)
    
    path = TextLine(title = u'Path',
        description = u'Path on Prefixed storage',
        default = u'',
        required = True)

                