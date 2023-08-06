### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based Quota package

$Id: interfaces.py 50387 2008-01-29 09:49:06Z cray $
"""

__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.interface import Interface
from zope.schema import Int, Field, Bool
from zope.app.component.interfaces import ILocalSiteManager
from zope.app.container.interfaces import IContained
from zope.app.container.constraints import ContainerTypesConstraint

class IQuotaControlled(Interface) :
    """ Object provide this interface to be controlled by quota """

class IQuotaData(Interface) :
    """ Custom quota parameters """
        
    quota = Int(
        title=u"Quota",
        description=u"Summarize Quota",
        default=100000000,
        required=True)
        
    check = Bool(
        title=u"Check quota",
        description=u"Quota will be check to be in alowed range",
        default=False,
        required=True)
        
    stat = Bool(
        title=u"Use statistic",
        description=u"Without this option events which can change quota will be ignored" ,
        default=True,
        required=True)

class IQuotaStat(Interface) :
    """ Quota Statistics """

    size = Int(
        title=u"Size",
        description=u"Current summarize size",
        default=0,
        readonly=True)

    count = Int(
        title=u"Count",
        description=u"Common object count",
        default=0,
        readonly=True)

    average = Int(
        title=u"Average Size",
        description=u"Current average size",
        default=0,
        readonly=True)

    min = Int(
        title=u"Minimum",
        description=u"Current minimum size",
        default=0,
        readonly=True)

    max = Int(
        title=u"Maximum",
        description=u"Current maximum size",
        default=0,
        readonly=True)


class IQuotaHandle(Interface) :
    def handleAdded(ob): 
        pass

    def handleModified(ob): 
        pass
 
    def handleRemoved(ob): 
        pass

    def reset(ob) :
        pass
        

class IQuotaAvailable(Interface) :
    pass

class IQuotaAnnotable(IQuotaAvailable) :
    pass

class IQuotaUtilitable(IQuotaAvailable) :
    pass

class IQuota(IQuotaData, IQuotaStat, IQuotaHandle, IQuotaAnnotable) :
    """ Quota """

class IQuotaUtility(IQuota) :
    """ Quota Utility """
    
class IQuotaAnnotation(IQuota) :
    """ Quota Annotation """
    
class IQuotaAll(Interface) :
    """ Enumerator for all Quota Utilities """

    def next() :
        pass 

    def __iter__() :
        pass

class IQuotaUtilities(Interface) :
    """ Enumerator for all Quota Utilities """

    def next() :
        pass 

    def __iter__() :
        pass

class IQuotaContained(IContained) :                
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager))

quotakey="ng.app.quota.quota.Quota"
        