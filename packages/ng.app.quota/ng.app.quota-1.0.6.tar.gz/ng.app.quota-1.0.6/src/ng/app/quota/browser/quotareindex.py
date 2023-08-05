### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteObjectEdit MixIn for the Zope 3 based ng.app.remotefs package

$Id: quotareindex.py 49790 2008-01-29 22:41:24Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49790 $"

import sys
from ng.lib.walk import BFSWalkTree
from ng.app.quota.interfaces import IQuota, IQuotaAnnotation
from histogram import Histogram
from zope.component import getUtilitiesFor
from zope.app.intid.interfaces import IIntIds
from zope.traversing.interfaces import IPhysicallyLocatable

class QuotaReindex(Histogram) :
    msg = ""
    def update(self) :
        super(QuotaReindex, self).update()
        if "reindex" in self.request :
            try :
                quota = IQuotaAnnotation(self.context)
                quota.reset()
                stat = quota.stat
                quota.stat = True
                if IQuotaAnnotation.providedBy(self.context) :
                    root = IPhysicallyLocatable(self.context).getNearestSite()
                else :
                    root = self.context
                for ob in BFSWalkTree(root) :
                    quota.handleAdded(ob)
                quota.stat = stat                    
            except Exception, msg :
                self.msg = msg                
                print sys.excepthook(*sys.exc_info())
                          

