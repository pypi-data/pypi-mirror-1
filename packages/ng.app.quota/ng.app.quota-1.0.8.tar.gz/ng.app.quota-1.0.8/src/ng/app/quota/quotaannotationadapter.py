### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAnnotationAdapter script for the Zope 3 based
ng.app.quota package

$Id: quotaannotationadapter.py 50802 2008-02-21 11:27:20Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50802 $"


from zope.annotation.interfaces import IAnnotations
from ng.app.quota.quota import Quota
from ng.app.quota.interfaces import quotakey


def QuotaAnnotationAdapter(context) :
    try :
        an = IAnnotations(context)[quotakey]
    except KeyError :
        an = IAnnotations(context)[quotakey] = Quota()
    return an
