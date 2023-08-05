### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based quota package

$Id: quota.py 49752 2008-01-27 20:25:18Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.app import zapi

from zope.interface import implements
from interfaces import IQuota,IQuotaContained
from zope.app.intid.interfaces import IIntIds
from ng.adapter.recordsize.interfaces import IRecordSize

from persistent import Persistent
from zope.app.container.contained import Contained
from BTrees.IOBTree import IOBTree
from interfaces import IQuotaAnnotable, IQuotaAnnotation
from zope.component.interfaces import ComponentLookupError

class QuotaError(RuntimeError) :
    """ Quota size exhausted """

class Quota(Contained,Persistent):
    __doc__ = IQuota.__doc__

    implements(IQuota,IQuotaContained,IQuotaAnnotable,IQuotaAnnotation)

    quota = 100000000
    size = 0
    average = 0
    count = 0 
    min = ""
    max = 0
    stat = True
    check = False       
    
    def __init__(self) :
        self.reset()
        
    def reset(self) :        
        self.osz = IOBTree()
        self.size = 0
        self.average = 0
        self.count = 0
        self.min = ""
        self.max = 0
            
    def handleAdded(self, object): 
        print "handleAdded:",self.__name__, object.__name__
        if self.stat :
            size = IRecordSize(object).size
            try :
                self.osz[zapi.getUtility(IIntIds, context=object).getId(object)] = size
            except ComponentLookupError,msg:
                print "QuotaAddFailed:",msg
            except KeyError :
                pass
            else :                                    
                self.count += 1
                self.size+=size
                self.average = float(self.size) / max(1,self.count)
                self.min = min(self.min,size)
                self.max = max(self.max,size)

                if self.check and self.size > self.quota :
                    raise QuotaError
 
    def handleModified(self, object): 
        if self.stat :
            size = IRecordSize(object).size
            try :
                key = zapi.getUtility(IIntIds, context=self).getId(object)
            except ComponentLookupError,msg:
                print "QuotaModifiedFailed:",msg
            else :
                try :
                    oldsize = self.osz[key]
                except KeyError :
                    pass            
                except ComponentLookupError,msg:
                    print "QuotaAddFailed:",msg
                else :
                    self.size-=oldsize
                    if size < self.max <= oldsize :
                        self.max = max(self.osz.values())
                    if oldsize <= self.min < size :
                        self.min = min(self.osz.values())

                try :
                    self.osz[zapi.getUtility(IIntIds, context=object).getId(object)] = size
                except KeyError,msg :
                    print "Can't find modified object in intid or localindex",msg

                self.size+=size
                self.min = min(self.min,size)
                self.max = max(self.max,size)

                try :
                    self.average = float(self.size) / self.count
                except ZeroDivisionError :
                    pass            

                if self.check and self.size > self.quota :
                    raise QuotaError
 
    def handleRemoved(self, object): 
        if self.stat :
            size = IRecordSize(object).size
            self.size-=size
            self.count -= 1
            self.average = float(self.size) / max(1,self.count)
    
            try :
                del self.osz[zapi.getUtility(IIntIds, context=object).getId(object)]
            except KeyError :
                pass
            except ComponentLookupError,msg:
                print "QuotaAddFailed:",msg
            else :
                if self.max <= size:
                    self.max = max(self.osz.values())
                if self.min >= size :
                    self.min = min(self.osz.values())
