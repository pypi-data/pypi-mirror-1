### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based remotefs package

$Id: interfaces.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Choice, Int
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
import datetime 
                
class IRemoteObjectAdd(Interface) :

    title = TextLine(title = u'Title',
        description = u'Title',
        default = u'',
        required = False)
    
    prefix = Choice(title = u'Connector',
        description = u'Name of remote connector utility',
        default = None,
        required = True,
        vocabulary = 'RemoteConnectorNames'
        )
                                                                                                      
    path = TextLine(title = u'Path',
        description = u'Path on Prefixed storage',
        default = u'',
        required = True)


class IRemoteObject(IRemoteObjectAdd) :

    date = Datetime(title = u'Date/Time',
        description = u'Date/Time',
        default = datetime.datetime.today(),
        required = False,
        readonly = True)

    def update() :
        """ Update IRemoteObject data via connector """

    
class IRemoteStat(Interface) :
    length = Int(title = u'File Length',
        default = 0,
        readonly = True,
        required = False)
    
    last_update = Datetime(title = u'Last Update',
        readonly = True,
        required = False)

