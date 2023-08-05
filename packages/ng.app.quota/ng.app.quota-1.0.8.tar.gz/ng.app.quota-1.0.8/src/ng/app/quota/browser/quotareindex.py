### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteObjectEdit MixIn for the Zope 3 based ng.app.remotefs package

$Id: quotareindex.py 50802 2008-02-21 11:27:20Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50802 $"

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
                          
        super(QuotaReindex, self).update()

