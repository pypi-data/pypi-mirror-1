### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Logout view

$Id: logout.py 51502 2008-08-06 17:55:26Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

import zope.component

class Logout(object) :
    
    def __init__(self,context,request) :
        super(Logout,self).__init__(context,request)
        

    def __call__(self) :
        self.request.response.expireCookie('userid', path="/")
        self.request.response.redirect("/")
        return ""

                    
        
