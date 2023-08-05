### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Update MixIn for the Zope 3 based ng.app.remotefs package

$Id: update.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov,2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"
 
from zope.interface import Interface
                
class Update(object) :
                        
    def getData(self) :
        return {}
        
    def setData(self,d) :
        self.context.update_list(d["update"])
        
        