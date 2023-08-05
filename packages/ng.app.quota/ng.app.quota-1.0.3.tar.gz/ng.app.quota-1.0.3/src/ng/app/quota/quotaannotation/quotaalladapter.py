### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAll class for the Zope 3 bases ng.app.quota

$Id: quotaalladapter.py 49750 2008-01-27 19:51:18Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49750 $"

from ng.app.quota.quota import Quota
from ng.app.quota.interfaces import IQuotaAll, IQuotaAnnotation, IQuotaUtility, IQuota,  quotakey
from zope.interface import implements
from zope.app.container.contained import IContained

class QuotaAllAdapter(object) :
    implements(IQuotaAll)

    def __init__(self,context) :
        self.context = context
        print "adapter init", getattr(self.context,'__name__',None)
        
                
    def handleAdded(self,ob): 
        try:    
            IQuotaAnnotation(self.context).handleAdded(ob)
        except TypeError :
            pass


        try:        
            IQuotaAll(IContained(self.context).__parent__).handleAdded(ob)
        except TypeError :
            IQuotaUtility(ob).handleAdded(ob)

    def handleModified(self,ob): 
        print "adapter 1", getattr(self.context,'__name__',None), ob.__name__
        
        try:    
            IQuotaAnnotation(self.context).handleModified(ob)
        except TypeError :
            pass
 
        print "adapter 2", getattr(self.context,'__name__',None), ob.__name__
        try:
            IQuotaAll(IContained(self.context).__parent__).handleModified(ob)
        except TypeError,msg :
            print "TypeError",msg
            print "CHECK ROOT", getattr(self.context,'__name__',None), ob.__name__
            IQuotaUtility(ob).handleModified(ob)
                        
    def handleRemoved(self, ob): 
        try:    
            IQuotaAnnotation(self.context).handleRemoved(ob)
        except TypeError :
            pass

        try:
            IQuotaAll(IContained(self.context).__parent__).handleRemoved(ob)
        except TypeError :
            IQuotaUtility(ob).handleRemoved(ob)

def Any2QuotaAllAdapter(context) :
    print "any quota"
    return IQuotaAll(IContained(context).__parent__)
                
    