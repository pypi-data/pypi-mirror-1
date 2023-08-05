### -*- coding: utf-8 -*- #############################################
#######################################################################
"""View class for the Zope 3 based remotefile package
View mix-in for view.html view :)

$Id: body.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

class Body(object) :
    """ View Mix-In """
    
    def body(self) :
        return self.context.body#.encode("UTF-8")
        