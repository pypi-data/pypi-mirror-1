### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.remotefs package

$Id: interfaces.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

from zope.interface import Interface
from zope.schema import Text

class IRemoteFile(Interface) :
    body = Text(title = u'File Body',
        description = u'FileBody',
        default = u'',
        readonly = True,
        required = False)

                