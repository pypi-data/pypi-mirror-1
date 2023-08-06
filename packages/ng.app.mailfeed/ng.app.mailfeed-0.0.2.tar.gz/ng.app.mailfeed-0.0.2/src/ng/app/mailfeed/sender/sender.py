### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: sender.py 53228 2009-06-11 07:43:50Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"

from zope.interface import implements
from zope.app.zapi import getUtility

from persistent import Persistent
from zope.app.container.contained import Contained 
from zope.sendmail.interfaces import IMailDelivery

from interfaces import ISender

class SenderBase(object):
    implements(ISender)

    mailfrom = u''
    delivery = u'Mail'

    def send(self,to,msg):
        getUtility(IMailDelivery,context=self,name=self.delivery).send(self.mailfrom,to,msg)
               
class SenderAnnotation(SenderBase, Persistent):
    """ SMTP sender annotation """

class Sender(SenderBase, Contained, Persistent):
    """ SMTP sender """
