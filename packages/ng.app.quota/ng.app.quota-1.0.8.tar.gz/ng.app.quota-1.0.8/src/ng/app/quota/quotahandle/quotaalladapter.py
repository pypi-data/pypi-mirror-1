### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAll class for the Zope 3 bases ng.app.quota

$Id: quotaalladapter.py 50802 2008-02-21 11:27:20Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50802 $"

from ng.app.quota.quota import Quota
from ng.app.quota.interfaces import IQuotaAll, IQuotaAnnotation, IQuota
from zope.interface import implements
from zope.app.container.contained import IContained
from zope.component import getUtilitiesFor


def QuotaAllAdapter(context) :
    try :
        yield IQuotaAnnotation(context)
    except TypeError :
        pass
        
    for quota in IQuotaAll(IContained(context).__parent__) :
        yield quota
        
def Site2QuotaAllAdapter(context) :
    try :
        yield IQuotaAnnotation(context)
    except TypeError :
        pass
        
    for name, quota in getUtilitiesFor(IQuota, context=context) :
        yield quota
        
    for quota in IQuotaAll(IContained(context).__parent__) :
        yield quota
        

def Any2QuotaAllAdapter(context) :
    return []
    