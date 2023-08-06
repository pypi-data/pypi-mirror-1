### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: mailtemplateannotableadapter.py 53228 2009-06-11 07:43:50Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"

from mailtemplate import MailTemplateAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import mailtemplateannotationkey
from zope.location.location import LocationProxy 


def IMailTemplateAnnotableAdapter(context) :

    try :
        an = IAnnotations(context)[mailtemplateannotationkey]
    except KeyError :
        an = IAnnotations(context)[mailtemplateannotationkey] = MailTemplateAnnotation()
    return LocationProxy(an, context, "++annotations++" + mailtemplateannotationkey)
