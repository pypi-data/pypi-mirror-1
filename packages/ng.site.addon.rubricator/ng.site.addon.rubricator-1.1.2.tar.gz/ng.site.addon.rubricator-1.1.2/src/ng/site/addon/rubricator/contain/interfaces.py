### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 52224 2008-12-27 15:03:11Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51242 $"
 

from zope.schema import Field
from zope.interface import Interface
#from ng.site.addon.tag.wave.interfaces import ITagRubricAnnotationAblePropagate
#from ng.site.addon.community.communityfactory.interfaces import ICommunityAnnotable
from ng.lib.containconstraint import ContainConstraint

#def forbidden(container) :
#    if ITagRubricAnnotationAblePropagate.providedBy(container) :
#        return False
#    elif ICommunityAnnotable.providedBy(container) :
#        return False
#    return True
#
#class ITagRubricAnnotationAbleForbidden(Interface) :
#    __parent__ = Field(constraint = forbidden)

class IDenyContainContent_(Interface) :
    """ """

class IDenyContainContent(IDenyContainContent_) :
    __parent__ = Field(constraint = ContainConstraint(IDenyContainContent_).deny)
    
    