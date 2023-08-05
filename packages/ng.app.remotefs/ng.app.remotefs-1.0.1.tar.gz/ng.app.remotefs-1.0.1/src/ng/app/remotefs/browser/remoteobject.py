### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteObjectEdit MixIn for the Zope 3 based ng.app.remotefs package

$Id: remoteobject.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

import sys

class RemoteObjectEdit(object) :

    msg = ""

    def update(self) :
        super(RemoteObjectEdit, self).update()
        if "update" in self.request :
            try :
                self.context.update(set())
            except Exception, msg :
                self.msg = msg                
                print sys.excepthook(*sys.exc_info())
                          

        
        
        
