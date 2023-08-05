### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based quota package

$Id: handle.py 49750 2008-01-27 19:51:18Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.app import zapi
from ng.app.quota.interfaces import IQuotaAll
from zope.component import ComponentLookupError
 
def handleAdded(object,event) :
    try :
        IQuotaAll(object).handleAdded(object)
    except TypeError :
        pass        

def handleModified(object,event) :
    try :
        IQuotaAll(object).handleModified(object)  
    except TypeError,msg :
        print "Type",msg
        pass
            
            
def handleRemoved(object,event) :
    try :
        IQuotaAll(object).handleRemoved(object)  
    except TypeError :
        pass
               