### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.remotefs package

$Id: interfaces.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

from zope.interface import Interface
from zope.schema import Text
                
class IRemoteUpdateForm(Interface) :
    """ Form used to update remotefiles """
    update = Text(title = u'Paths to update',
        description = u'Paths to update',
        default = u'',
        required = False
    )

class IRemoteUpdate(Interface) :
    """ Interface to update remote files """

    def update_list(paths) :
        """ Update files of paths """    

    def update_list_urls(paths) :
        """ Update list of paths """    

    def update_all() :
        """ Update all files """    

