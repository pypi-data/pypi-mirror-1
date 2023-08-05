### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAdapter class for the Zope 3 based ng.app.quota.quotaannotation package

$Id: quotaadapter.py 49750 2008-01-27 19:51:18Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49750 $"


from zope.annotation.interfaces import IAnnotations
from ng.app.quota.quota import Quota
from ng.app.quota.interfaces import quotakey

def QuotaAdapter(context) :
    print "Anno-Qouta",getattr(context,'__name__',None)
    try :
        an = IAnnotations(context)[quotakey]
    except KeyError :
        an = IAnnotations(context)[quotakey] = Quota()
    return an
