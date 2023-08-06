### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaUtilityAdapter script for the Zope 3 based ng.app.quota package

$Id: quotautilityadapter.py 50592 2008-02-07 06:53:24Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50592 $"


from zope.component import getUtilitiesFor
from interfaces import IQuota


def QuotaUtilityAdapter(context) :
    try :
        return ( y for x,y in getUtilitiesFor(IQuota, context=context) ).next()
    except StopItteration :
        raise TypeError        
