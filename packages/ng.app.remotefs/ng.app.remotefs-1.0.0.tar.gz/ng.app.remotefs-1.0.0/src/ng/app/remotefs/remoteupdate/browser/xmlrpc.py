### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: xmlrpc.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"
 
from zope.interface import Interface
                
class XMLRPCUpdate(object) :
                        
    def update(self,items) :
        if items :
            self.context.update_list_urls(items)
            return "OK!"
        return "We must use not empty items list"            
        
