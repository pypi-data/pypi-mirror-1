### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAdapter class for the Zope 3 based ng.app.quota.quotaannotation package

$Id: quotaannotationadapter.py 49790 2008-01-29 22:41:24Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49790 $"


from zope.annotation.interfaces import IAnnotations
from ng.app.quota.quota import Quota
from ng.app.quota.interfaces import quotakey

def QuotaAnnotationAdapter(context) :
    try :
        an = IAnnotations(context)[quotakey]
    except KeyError :
        an = IAnnotations(context)[quotakey] = Quota()
    return an
