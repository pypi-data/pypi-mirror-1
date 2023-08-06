### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter for the Zope 3 based product package

$Id: openiderrormessageadapter.py 51886 2008-10-21 05:16:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51886 $"

from openiderrormessage import OpenIDErrorMessage
from zope.annotation.interfaces import IAnnotations 
from interfaces import openiderrormessagekey

def OpenIDErrorMessageAdapter(context) :

    try :
        an = IAnnotations(context)[openiderrormessagekey]
    except KeyError :
        an = IAnnotations(context)[openiderrormessagekey] = OpenIDErrorMessage()
    return an
