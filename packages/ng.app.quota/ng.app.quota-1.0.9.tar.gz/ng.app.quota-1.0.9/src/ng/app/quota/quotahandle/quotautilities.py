### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAdapter class for the Zope 3 based ng.app.quota.quotahandle package

$Id: quotautilities.py 51043 2008-04-29 02:23:07Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51043 $"


from zope.component import getUtilitiesFor
from interfaces import IQuota


class QuotaAdapter(object) :

    def __init__(self,context) :
        self.context = context
        self.quotas = [ y for x,y in getUtilitiesFor(IQuota, context=context) ]

    def handleAdded(self,ob): 
        for quota in self.quotas :
            quota.handleAdded(ob)

    def handleModified(self,ob): 
        for quota in self.quotas :
            quota.handleModified(ob)
 
    def handleRemoved(self,ob): 
        for quota in self.quotas :
            quota.handleRemoved(ob)
