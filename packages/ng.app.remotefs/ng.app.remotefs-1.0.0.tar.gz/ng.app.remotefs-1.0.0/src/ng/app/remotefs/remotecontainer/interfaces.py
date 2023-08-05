### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.remotefs package

$Id: interfaces.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Choice, Password
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint

class IRemoteContainerContent(Interface) :
    pass

class IRemoteContainer(IContainer) :
    descriptors = Field()

    def __setitem__(name, object):
            """Add a Registry Item object."""
        
    __setitem__.precondition = ItemTypePrecondition(IRemoteContainerContent)

class IRemoteDescriptorContainerContent(Interface):
    pass

class IRemoteDescriptorContainer(IContainer) :
    def __setitem__(name, object):
            """Add a Registry Item object."""

    __parent__ = Field(
            constraint = ContainerTypesConstraint(IRemoteContainer))
        
    __setitem__.precondition = ItemTypePrecondition(IRemoteDescriptorContainerContent)

class IRemoteDescriptor(IContained,IRemoteDescriptorContainerContent) :
    """ Registry item about remote files """
    
    
    isordinal = Bool(title=u"Обычный файл",
                    description=u"Установлено, если файл обычный и создан через вебинтерфейс",
                    default=True,
                    required=False)

    isdeleted = Bool(title=u"Файл удален",
                    description=u"Установлено, если файл существует в репозитории, но удален через веб интерфейс",
                    default=False,
                    required=False)
    
                