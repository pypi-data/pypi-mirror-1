### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the OpenId view

$Id: logincredentials.py 52466 2009-02-06 13:31:38Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52466 $"

from zope.interface import Interface, implements
from zope.publisher.browser import BrowserView
from zope.traversing.browser import absoluteURL
from persistent import Persistent

from zope import interface
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog

from urllib import quote
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContained
from interfaces import ILoginCredentialsPlugin, ICookieCredentialsPlugin, IProfileLoginInformation
from ng.content.profile.profileannotation.interfaces import IProfileAnnotation 
from interfaces import IOpenIDErrorMessage
from crypt import crypt

class LoginCredentialsPlugin(Contained,Persistent) :

    implements(ICredentialsPlugin,IContained, ILoginCredentialsPlugin)

    cookie_max_age = 60*60*24*365
    cookie_path = "/"
    prefix = "openid."
    

    def extractCredentials(self,request) :
        if request.form.has_key('login')  and request.form.has_key('password') :
            login =  request.form['login']
            if login :
              if request.form.has_key('save') :
                  request.response.setCookie('login',login,path=self.cookie_path,max_age=self.cookie_max_age)

              message = IOpenIDErrorMessage(request)
              for profile in getUtility(ICatalog,context=self) \
                            .searchResults(
                                profile=( self.prefix+unicode(login), self.prefix+unicode(login) + u"\uffff" )
                            ) :
                  info = IProfileAnnotation(profile)                          
                  
                  if info.password == crypt(request.form['password'],info.password) :
                      getUtility(ICookieCredentialsPlugin, context=self).setsession(login,request)
                      return (login,request)
                  else :
                      message.title = u"Wrong password" 
                      message.message = u"Dismiss password entered, try again"
                      message.haserror = True                        
                      return None                      
              else :
                message.title = u"User is unknown" 
                message.message = u"Check entered login or registered"
                message.haserror = True                        

        return None
        
    def challenge(self, request) :
        pass
        
    def logout(self, request) :
        pass

                    
            
