### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: openidauthenticator.py 52466 2009-02-06 13:31:38Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52466 $"

from zope.interface import Interface, implements
from persistent import Persistent
from zope.app.authentication.interfaces import IAuthenticatorPlugin, IQuerySchemaSearch
from zope.app.authentication.principalfolder import PrincipalInfo, ISearchSchema

from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from ng.content.profile.profileannotation.interfaces import IProfileAnnotation 
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.interfaces import IAdding
from zope.app.container.browser.adding import Adding
from ng.site.addon.profile.profilefactory.profile import ProfileCreate
from zope.lifecycleevent import ObjectCreatedEvent
from zope.event import notify
from interfaces import IOpenIDAuthenticatorPlugin

class OpenIDAuthenticatorPlugin(Contained, Persistent) :

    implements(IAuthenticatorPlugin, IQuerySchemaSearch, IContained, IOpenIDAuthenticatorPlugin)

    prefix = u"openid."
    profile = u'http://greenfuture.ru/profile/%s/@@register.html'
    schema = ISearchSchema

    def authenticateCredentials(self, credentials):

      try :
        id, request = credentials
      except TypeError :
        return None
                
      user = self.get(id)
      if not user :
          container = getUtility(IContainer,'profile',context=self)
          try :
              name = str(max(( int(key) for key in container.keys() if key.isdigit() ))+1)
          except ValueError :
              name = '0'    
              
          content = ProfileCreate(self.prefix+id)
          notify(ObjectCreatedEvent(content))
                        
          container[name] = content
          if self.profile :
            request.response.redirect(self.profile % name)
      return user

    def search(self, query, start=None, batch_size=None) :
      id = query['search']
      for profile in getUtility(ICatalog,context=self) \
                          .searchResults(
                              profile=( self.prefix+unicode(id), self.prefix+unicode(id) + u"\uffff" )
                          ) :
          info = IProfileAnnotation(profile)                          
          yield info.userid[len(self.prefix):]
          
    def get(self, id) :
      for profile in getUtility(ICatalog,context=self) \
                          .searchResults(
                              profile=( self.prefix+unicode(id), self.prefix+unicode(id) )
                          ) :
          info = IProfileAnnotation(profile)                          
          return PrincipalInfo(
            info.userid[len(self.prefix):],
            info.userid[len(self.prefix):],
            info.nickname,
            profile.abstract)
        
    def principalInfo(self,id) :
      return self.get(id)
      