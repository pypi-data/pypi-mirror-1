### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter for the Zope 3 based product package

$Id: openiderrormessageadapter.py 52115 2008-12-22 19:10:52Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52115 $"

from openiderrormessage import OpenIDErrorMessage
from zope.annotation.interfaces import IAnnotations 
from interfaces import openiderrormessagekey

def OpenIDErrorMessageAdapter(context) :

    try :
        an = IAnnotations(context)[openiderrormessagekey]
    except KeyError :
        an = IAnnotations(context)[openiderrormessagekey] = OpenIDErrorMessage()
    return an
