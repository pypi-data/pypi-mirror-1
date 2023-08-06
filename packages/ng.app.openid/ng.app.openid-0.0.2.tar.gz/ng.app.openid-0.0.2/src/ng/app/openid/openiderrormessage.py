### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: openiderrormessage.py 52115 2008-12-22 19:10:52Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52115 $"

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
                  