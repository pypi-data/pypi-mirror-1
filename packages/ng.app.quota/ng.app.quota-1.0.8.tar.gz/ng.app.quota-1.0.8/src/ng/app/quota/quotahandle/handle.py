### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based quota package

$Id: handle.py 50802 2008-02-21 11:27:20Z cray $
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
    for quota in IQuotaAll(ob) :
        quota.handleModified(ob)

def handleRemoved(ob,event) :
    for quota in IQuotaAll(ob) :
        quota.handleRemoved(ob)
               