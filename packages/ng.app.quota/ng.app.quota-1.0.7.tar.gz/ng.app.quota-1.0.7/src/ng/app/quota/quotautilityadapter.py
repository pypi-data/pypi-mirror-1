### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAdapter class for the Zope 3 based ng.app.quota.quotaannotation package

$Id: quotautilityadapter.py 49891 2008-02-02 15:36:58Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49891 $"


from zope.component import getUtilitiesFor
from interfaces import IQuota

def QuotaUtilityAdapter(context) :
    try :
        return ( y for x,y in getUtilitiesFor(IQuota, context=context) ).next()
    except StopItteration :
        raise TypeError        
