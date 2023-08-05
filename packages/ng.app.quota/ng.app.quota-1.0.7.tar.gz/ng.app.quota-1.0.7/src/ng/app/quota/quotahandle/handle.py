### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based quota package

$Id: handle.py 49891 2008-02-02 15:36:58Z cray $
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
               