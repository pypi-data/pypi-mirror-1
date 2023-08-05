### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.remotefs package

$Id: interfaces.py 49290 2008-01-08 16:51:54Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49290 $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, Datetime, Password

class IRemoteConnector(Interface) :

    prefix = TextLine(title = u'Connection Prefix',
        description = u'Connection prefix',
        default = u'https://code.keysolutions.ru/svn/',
        required = True
        )

    realm = TextLine(title = u'Realm',
        description = u'Realm',
        default = u'',
        required = False
        )

    username = TextLine(title = u'Username',
        description = u'Username',
        default = u'',
        required = False
        )

    password = Password(title = u'Password',
        description = u'Password',
        default = u'',
        required = False
        )

    def update(prefix,path) :
        """ Return body of prefix + path resource """

    def list(prefix,path) :
        """ Return sublist """
        