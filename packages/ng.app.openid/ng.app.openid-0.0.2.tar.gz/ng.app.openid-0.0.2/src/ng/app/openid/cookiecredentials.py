### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the OpenId view

$Id: cookiecredentials.py 52425 2009-01-31 16:37:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52425 $"

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
from interfaces import ICookieCredentialsPlugin, IOpenIDErrorMessage
from ng.skin.base.page.exception.redirectexception import RedirectException

import time, md5, random, base64, marshal

hash = str(random.random())

class CookieCredentialsPlugin(Contained,Persistent) :

    implements(ICredentialsPlugin,IContained, ICookieCredentialsPlugin)

    cookie_path = u'/'
    timeout = 900
    
    def extractCredentials(self,request) :
        if request.cookies.has_key('userid') :
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

        return None

    def setsession(self,url,request) :
        request.response.setCookie('userid', self.encodeCookie(url), path=self.cookie_path)
        
        
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
            return marshal.loads(base64.urlsafe_b64decode(data[32:]))
            
        raise ValueError
                    
            
