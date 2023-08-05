### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.remotefs package

$Id: interfaces.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

from zope.interface import Interface
from zope.schema import TextLine, Choice

                
class IRemoteFactoryItem(Interface) :

    regexp = TextLine(title = u'File match',
        description = u'Regular Expression to match File Format',
        default = '^.*$',
        required = True,
        readonly = False)

    factory = Choice(
        title=u'Factory',
        description=u'Name class for factory',
        vocabulary='MapperInterfaceName',
        required=True)
