### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The remoteconnectorvocabulary factory for the Zope 3 based ng.app.remotefs
package

$Id: remoteconnectorvocabulary.py 49266 2008-01-08 12:34:56Z cray $ """ 

__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

from zope.schema.vocabulary import SimpleVocabulary
from ng.app.remotefs.remoteconnector.interfaces import IRemoteConnector
from zope.app.zapi import getUtilitiesFor

def remoteconnectorvocabulary(context):
    """Get utitlity vocabulary for IRemoteConnector"""
    return SimpleVocabulary.fromValues(
        (x for (x,y) in getUtilitiesFor(IRemoteConnector, context) )
        )
