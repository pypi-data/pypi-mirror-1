### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Update MixIn for the Zope 3 based ng.app.remotefs package

$Id: update.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov,2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"
 
from zope.interface import Interface
                
class Update(object) :
                        
    def getData(self) :
        return {}
        
    def setData(self,d) :
        self.context.update_list(d["update"])
        
        