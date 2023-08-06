### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: mailtemplateutilitableadapter.py 53228 2009-06-11 07:43:50Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"

from zope.app.zapi import getUtility
from mailtemplate import MailTemplate
from interfaces import IMailTemplate, IMailTemplateUtilitable

def IMailTemplateUtilitableAdapter(context) :
    return getUtility(IMailTemplate,context=context,name=IMailTemplateUtilitable(context).mailtemplate)
    