### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: openiderrormessage.py 51961 2008-10-23 21:46:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51961 $"

from zope.interface import Interface, implements
from interfaces import IOpenIDErrorMessage

class OpenIDErrorMessage(object) :
    implements(IOpenIDErrorMessage) 
    
    
    title = u""
    message = u""
    haserror = False

    def __init__(self,title=u"",message=u"") :
        self.title = title
        self.message = message
        if title or message :
            self.haserror = True
                  