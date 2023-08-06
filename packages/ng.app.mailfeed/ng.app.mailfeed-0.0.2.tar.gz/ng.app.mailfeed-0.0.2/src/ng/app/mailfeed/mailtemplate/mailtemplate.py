### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: mailtemplate.py 53588 2009-08-13 21:12:31Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53588 $"

from zope.interface import implements
from persistent import Persistent
from zope.app.container.contained import Contained 

from interfaces import IMailTemplate

class MailTemplateBase(object):
    implements(IMailTemplate)

    subject = u""
    body = u""
    charset = u"UTF-8"
    mimetype = u"text/plain"
    #converter 
    #mimeadapter = Choice(
    isadaptive = True

    def apply(self,**kw):
        return "Content-Type: %s; charset=%s\n" % (self.mimetype,self.charset) + \
            "Subject: %s\n\n" %  (self.subject % kw,) + \
            self.body % kw + "\n"
               
class MailTemplateAnnotation(MailTemplateBase, Persistent):
    """ Mail template annotation """

class MailTemplate(MailTemplateBase, Contained, Persistent):
    """ Mail template """
