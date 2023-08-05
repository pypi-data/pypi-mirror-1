### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAdapter class for the Zope 3 based ng.app.quota.quotaannotation package

$Id: quotautilityadapter.py 49790 2008-01-29 22:41:24Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49790 $"


from zope.component import getUtilitiesFor
from interfaces import IQuota

def QuotaUtilityAdapter(context) :
    try :
        return ( y for x,y in getUtilitiesFor(IQuota, context=context) ).next()
    except StopItteration :
        raise TypeError        
