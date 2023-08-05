### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Wrapper arround SVN

$Id: svnwrapper.py 49604 2008-01-21 12:17:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49604 $"

import os
import re
import datetime
import time

def info(url) :
    """Return node info"""
    info = os.popen("svn info '%s'" % url).read()
    return re.compile("""Path: (?P<path>.*)(
Name: (?P<name>.*))?
URL: (?P<url>.*)
Repository Root: (?P<root>.*)
Repository UUID: (?P<uuid>.*)
Revision: (?P<rev>.*)
Node Kind: (?P<kind>.*)
Last Changed Author: (?P<author>.*)
Last Changed Rev: (?P<lastrev>.*)
Last Changed Date: (?P<date>.*)""",re.M).search(info).groupdict()
  
def date(url) :
    """ Return time date """
    return datetime.datetime(*time.strptime(info(url)["date"][0:19],"%Y-%m-%d  %H:%M:%S")[0:6])

def isdir(url) :
    """ Return True if node is not terminal """
    return info(url)["kind"] == "directory"
    
def list(url) :
    """ Return node list """
    return os.popen("svn list '%s'" %url).read().split("\n")[0:-1]
    
def cat(url) :
    """ Return node body """
    return os.popen("svn cat '%s'" %url).read()

if __name__ == '__main__' :    
    print isdir('https://code.keysolutions.ru/svn/ks/trunk/ks/doc/article/vocabulary')    
    print list('https://code.keysolutions.ru/svn/ks/trunk/ks/doc/article/vocabulary')    
    print cat('https://code.keysolutions.ru/svn/ks/trunk/ks/doc/article/vocabulary/vocabulary.txt')    
