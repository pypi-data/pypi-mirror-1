### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteObjectEdit MixIn for the Zope 3 based ng.app.remotefs package

$Id: quotareindex.py 49750 2008-01-27 19:51:18Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49750 $"

import sys
from ng.lib.walk import BFSWalkTree
from ng.app.quota.interfaces import IQuota, IQuotaAnnotation
from histogram import Histogram
from zope.component import getUtilitiesFor
from zope.app.intid.interfaces import IIntIds

class QuotaReindex(Histogram) :

    msg = ""

    def update(self) :
        super(QuotaReindex, self).update()
        if "reindex" in self.request :
            try :
                quota = IQuotaAnnotation(self.context)
                quota.reset()
                if IQuotaAnnotation.providedBy(self.context) :
                    for name,intids in getUtilitiesFor(IIntIds,context=self.context) :
                        for key in intids :
                            quota.handleAdded(intids.queryObject(key))
                else :
                    for ob in BFSWalkTree(self.context) :
                        quota.handleAdded(ob)
            except Exception, msg :
                self.msg = msg                
                print sys.excepthook(*sys.exc_info())
                          

        
        
        
