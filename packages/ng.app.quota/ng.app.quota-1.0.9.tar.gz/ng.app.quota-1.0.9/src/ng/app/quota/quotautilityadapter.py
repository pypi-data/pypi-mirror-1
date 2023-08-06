### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaUtilityAdapter script for the Zope 3 based ng.app.quota package

$Id: quotautilityadapter.py 51043 2008-04-29 02:23:07Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51043 $"


from zope.component import getUtilitiesFor
from interfaces import IQuota


def QuotaUtilityAdapter(context) :
    try :
        return ( y for x,y in getUtilitiesFor(IQuota, context=context) ).next()
    except StopItteration :
        raise TypeError        
