### -*- coding: utf-8 -*- #############################################
#######################################################################
"""View class for the Zope 3 based remotefile package
View mix-in for view.html view :)

$Id: body.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

class Body(object) :
    """ View Mix-In """
    
    def body(self) :
        return self.context.body#.encode("UTF-8")
        