### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Exceptions for the Zope 3 based ng.app.remotefs package

$Id: exceptions.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

class RemoteFSError(RuntimeError) :
    pass 

class RemoteFSInvalidObject(LookupError,RemoteFSError) :
    pass
                    
                