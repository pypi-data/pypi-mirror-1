### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51886 2008-10-21 05:16:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51242 $"
 
from zope.interface import Interface
from ng.utility.interfacewave.interfaces import IPropagateInterface
from ng.app.rubricator.tag.tagrubricannotation.interfaces import ITagRubricAnnotationAble
from ng.app.rubricator.tag.tagitemannotation.interfaces import ITagItemAnnotationAble
                            
class ITagRubricAnnotationAblePropagate(ITagRubricAnnotationAble,IPropagateInterface) :
    """ Interface for rubric annotable by tag """
    
#class ITagItemAnnotationAblePropagate(ITagItemAnnotationAble,IPropagateInterface) :
#    """ """