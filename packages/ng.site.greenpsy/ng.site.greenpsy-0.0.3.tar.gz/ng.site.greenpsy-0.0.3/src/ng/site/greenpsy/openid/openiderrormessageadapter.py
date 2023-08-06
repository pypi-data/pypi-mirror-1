### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter for the Zope 3 based product package

$Id: openiderrormessageadapter.py 51961 2008-10-23 21:46:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51961 $"

from openiderrormessage import OpenIDErrorMessage
from zope.annotation.interfaces import IAnnotations 
from interfaces import openiderrormessagekey

def OpenIDErrorMessageAdapter(context) :

    try :
        an = IAnnotations(context)[openiderrormessagekey]
    except KeyError :
        an = IAnnotations(context)[openiderrormessagekey] = OpenIDErrorMessage()
    return an
