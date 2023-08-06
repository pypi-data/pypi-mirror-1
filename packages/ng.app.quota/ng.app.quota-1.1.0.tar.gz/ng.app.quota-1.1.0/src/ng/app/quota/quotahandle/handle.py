### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based quota package

$Id: handle.py 52853 2009-04-07 13:06:12Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.app import zapi
from ng.app.quota.interfaces import IQuotaAll
 
def handleAdded(ob,event) :
    for quota in IQuotaAll(ob) :
        quota.handleAdded(ob)

def handleModified(ob,event) :
    try :
        for quota in IQuotaAll(ob) :
            quota.handleModified(ob)
    except AttributeError,msg :
        print "QuotaError 2:",msg

def handleRemoved(ob,event) :
    for quota in IQuotaAll(ob) :
        quota.handleRemoved(ob)

               