### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the OpenId view

$Id: openidcredentials.py 51961 2008-10-23 21:46:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51961 $"

from zope.interface import Interface, implements
from zope.publisher.browser import BrowserView
from openid.consumer.consumer import Consumer
from openid.consumer.consumer import FAILURE, SUCCESS, CANCEL, SETUP_NEEDED
from openid.store.memstore import MemoryStore
from openid.consumer.discover import DiscoveryFailure

from zope.traversing.browser import absoluteURL
from persistent import Persistent

from zope import interface
from zope.app.authentication.interfaces import ICredentialsPlugin
from urllib import quote
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContained
from interfaces import IOpenIDCredentialsPlugin, IOpenIDErrorMessage
from ng.skin.base.page.exception.redirectexception import RedirectException

import time, md5, random, base64, marshal

session = {}
store = MemoryStore()
hash = str(random.random())

openid_template = {
    "AOL" :    		"openid.aol.com/%s",
    "Blogger" :		"%s.blogspot.com",
    "Flickr" : 		"www.flickr.com/photos/%s",
    "LiveDoor" :    	"profile.livedoor.com/%s",
    "LiveJournal" : 	"%s.livejournal.com",
    "SmugMug" :     	"%s.smugmug.com",
    "Technorati" :  	"technorati.com/people/technorati/%s",
    "Vox" :    		"%s.vox.com",
    "Yahoo" :  		"http://%s.yahoo.com",
    "WordPress" :  	"%s.wordpress.com",
    "Yandex" :		"http://openid.yandex.ru/%s",
}
        
class OpenIDCredentialsPlugin(Contained,Persistent) :

    implements(ICredentialsPlugin,IContained, IOpenIDCredentialsPlugin)

    vh_path = u'/++skin++greenpsy/Psy/++vh++http:greenfuture.ru:80/++//'
    vh_site = u'http://greenfuture.ru/'
    cookie_path = u'/'
    timeout = 900
    cookie_max_age = 60*60*24*365
    
    def getURL(self,request) :
        return self.vh_site + quote(str(request['PATH_INFO'][len(self.vh_path):]))

    def extractCredentials(self,request) :
        consumer = Consumer(session, store)
        print session
        if request.form.has_key('openid') :
            print "openid"
            openid = request.form['openid']
            if request.form.has_key('save') :
                request.response.setCookie('openid',request.form['openid'],path=self.cookie_path,max_age=self.cookie_max_age)
                request.response.setCookie('provider',request.form['provider'],path=self.cookie_path,max_age=self.cookie_max_age)

            try :
                openid = openid_template[request.form['provider']] % openid
            except KeyError :
                pass
            print "openid id:", openid                    
            try :
                authrequest = consumer.begin(openid)    
            except DiscoveryFailure, msg :
                message = IOpenIDErrorMessage(request)
                message.title = u"OpenID Server Not Found"
                message.message = msg
                message.haserror = True
            else :            
                #request.response.redirect(
                raise RedirectException(
                    authrequest.redirectURL(
                        self.vh_site, #self.getURL(request),
                        self.getURL(request)
                        )
                    )
                print session                
        elif request.cookies.has_key('userid') :
            print "check cookie stage"
            try :
                t, identity = self.decodeCookie(request.cookies['userid'])
            except ValueError :
                print "decode userid error"
            else :                              
                t = time.time() - t

                if t < self.timeout :
                    if t > self.timeout / 10 :
                        request.response.setCookie('userid',self.encodeCookie(identity),path=self.cookie_path)

                    return (identity,request)

        if request.form.has_key('janrain_nonce') :
            print "check second stage"
            print type(request.form)
            print self.getURL(request)
            res = consumer.complete(
                request.form, 
                self.getURL(request)
                )
                
            print res.status
            if res.status == SUCCESS :
                print res.signed_fields
                print res.message
                print res.getDisplayIdentifier()
                print res.identity_url
                
                request.response.setCookie('userid',self.encodeCookie(res.identity_url),path=self.cookie_path)
                return (res.identity_url,request)

        return None
        
    def challenge(self, request) :
        pass
        
    def logout(self, request) :
        pass

    def encodeCookie(self,identity) :
        md5sum = md5.md5(hash)                         
        data = base64.urlsafe_b64encode(marshal.dumps((time.time(),identity)))
        md5sum.update(data)
        return md5sum.hexdigest()+data

    def decodeCookie(self,data) :
        data = str(data)
        md5sum = md5.md5(hash)
        md5sum.update(data[32:])                    
        if md5sum.hexdigest() == data[:32] :
            print data[32:],type(data[32:])
            return marshal.loads(base64.urlsafe_b64decode(data[32:]))
            
        raise ValueError
                    
            
