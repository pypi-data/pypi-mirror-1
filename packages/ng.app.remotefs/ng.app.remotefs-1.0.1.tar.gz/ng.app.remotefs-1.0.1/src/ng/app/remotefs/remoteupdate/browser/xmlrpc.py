### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: xmlrpc.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"
 
from zope.interface import Interface
                
class XMLRPCUpdate(object) :
                        
    def update(self,items) :
        if items :
            self.context.update_list_urls(items)
            return "OK!"
        return "We must use not empty items list"            
        
