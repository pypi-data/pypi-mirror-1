### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaUtilityAdapter script for the Zope 3 based ng.app.quota package

$Id: quotautilityadapter.py 50802 2008-02-21 11:27:20Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50802 $"


from zope.component import getUtilitiesFor
from interfaces import IQuota


def QuotaUtilityAdapter(context) :
    try :
        return ( y for x,y in getUtilitiesFor(IQuota, context=context) ).next()
    except StopItteration :
        raise TypeError        
