### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based openid credentials and authenticators

$Id: interfaces.py 51961 2008-10-23 21:46:14Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51222 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, URI, Datetime, Object, Int

class IOpenIDAuthenticatorPlugin(Interface) :

    prefix = TextLine(title=u"Prefix",default=u"openid.")
    
    profile = TextLine(title=u"Profile URL",default=u"http://greenfuture.ru/profile/%s/@@commonedit.html")
    
class IOpenIDCredentialsPlugin(Interface) :

    vh_path = TextLine(title=u"Path to virtual host",default=u"")
    
    vh_site = TextLine(title=u"Base virtual host URL",default=u"")
    
    timeout = Int(title=u'Credentials timeout', default=900, min=0)

    cookie_path = TextLine(title=u"Path to set cookie",default=u"/")

    cookie_max_age = Int(title=u'Form parameters lifetime', default=31536000, min=0)

class IOpenIDErrorMessage(Interface) :

    title = TextLine(title=u"Error title")
    
    message = Text(title=u"Error description")

    haserror = Bool(title=u"Shit Happened")
    
openiderrormessagekey = "openiderrormessagekey"    