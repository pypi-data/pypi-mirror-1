### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAnnotationAdapter script for the Zope 3 based
ng.app.quota package

$Id: quotaannotationadapter.py 50592 2008-02-07 06:53:24Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50592 $"


from zope.annotation.interfaces import IAnnotations
from ng.app.quota.quota import Quota
from ng.app.quota.interfaces import quotakey


def QuotaAnnotationAdapter(context) :
    try :
        an = IAnnotations(context)[quotakey]
    except KeyError :
        an = IAnnotations(context)[quotakey] = Quota()
    return an
