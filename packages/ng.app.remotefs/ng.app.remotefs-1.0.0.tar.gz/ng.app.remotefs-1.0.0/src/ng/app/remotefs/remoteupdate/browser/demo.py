#! /usr/bin/python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Demo script for update remote objects provided by Zope 3 based
ng.app.remotefs package

$Id: demo.py 49266 2008-01-08 12:34:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49266 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy

from xmlrpclib import ServerProxy, Error
import sys

server = ServerProxy(sys.argv[1])

try:
    print "Result:",server.update(sys.stdin.readlines())
except Error, v:
    print "ERROR", v

