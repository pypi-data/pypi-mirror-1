### -*- coding: utf-8 -*- #############################################
#######################################################################
"""View class for the Zope 3 based remotefile package
View mix-in for view.html view :)

$Id: view.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

class View(object) :
    """ View Mix-In """

    
    def __init__(self,*kv,**kw) :
        super(View,self).__init__(*kv,**kw)
        if self.request.form.has_key('UPDATE_SUBMIT') :
            self.context.update()

    @property
    def length(self) :
        return len(self.context.body)