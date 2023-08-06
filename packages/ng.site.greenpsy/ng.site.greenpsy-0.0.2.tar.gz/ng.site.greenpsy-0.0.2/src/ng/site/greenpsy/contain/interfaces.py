### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51886 2008-10-21 05:16:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51242 $"
 

from zope.schema import Field
from zope.interface import Interface
from ng.site.greenpsy.wave.interfaces import ITagRubricAnnotationAblePropagate
from ng.site.content.communityfactory.interfaces import ICommunityAnnotable

def forbidden(container) :
    if ITagRubricAnnotationAblePropagate.providedBy(container) :
        return False
    elif ICommunityAnnotable.providedBy(container) :
        return False
    return True

class ITagRubricAnnotationAbleForbidden(Interface) :
    __parent__ = Field(constraint = forbidden)

    