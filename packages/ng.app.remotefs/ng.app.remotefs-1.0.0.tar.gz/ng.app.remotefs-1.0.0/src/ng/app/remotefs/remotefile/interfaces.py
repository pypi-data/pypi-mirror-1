### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.remotefs package

$Id: interfaces.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

from zope.interface import Interface
from zope.schema import Text

class IRemoteFile(Interface) :
    body = Text(title = u'File Body',
        description = u'FileBody',
        default = u'',
        readonly = True,
        required = False)

                