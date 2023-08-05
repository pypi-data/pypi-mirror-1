### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Exceptions for the Zope 3 based ng.app.remotefs package

$Id: exceptions.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

class RemoteFSError(RuntimeError) :
    pass 

class RemoteFSInvalidObject(LookupError,RemoteFSError) :
    pass
                    
                