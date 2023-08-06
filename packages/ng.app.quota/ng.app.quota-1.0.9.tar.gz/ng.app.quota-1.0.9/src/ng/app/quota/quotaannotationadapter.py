### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAnnotationAdapter script for the Zope 3 based
ng.app.quota package

$Id: quotaannotationadapter.py 51043 2008-04-29 02:23:07Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51043 $"


from zope.annotation.interfaces import IAnnotations
from ng.app.quota.quota import Quota
from ng.app.quota.interfaces import quotakey


def QuotaAnnotationAdapter(context) :
    try :
        an = IAnnotations(context)[quotakey]
    except KeyError :
        an = IAnnotations(context)[quotakey] = Quota()
    return an
