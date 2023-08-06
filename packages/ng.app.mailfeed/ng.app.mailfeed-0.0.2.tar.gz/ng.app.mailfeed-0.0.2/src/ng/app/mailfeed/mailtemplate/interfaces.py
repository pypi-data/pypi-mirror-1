### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 53589 2009-08-14 20:10:19Z cray $
"""
__author__  = "Ilshad Habibullin, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53589 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Bool, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint

#from ng.app.converter.convertervocabulary import ConverterVocabulary

from ng.lib.utilityvocabulary import UtilityVocabulary
                
class IMailTemplate(Interface) :
    """ Base schema for mail template (abstract) """

    subject = TextLine(
        title=u'Subject',
        required=True,
        default=u'')

    body = Text(
        title=u'Body',
        required=True,
        default=u'')

    charset = TextLine(
        title=u'Charset',
        required=True,
        default=u'UTF-8')

    mimetype = TextLine(
        title=u'MIME Type',
        required=False,
        default=u'text/plain')

#    converter = Choice(
#        title=u'Select converter to html',
#        source=ConverterVocabulary(),
#        required=False)

#    mimeadapter = Choice(
#        title=u'Select converter to MIME',
#        source=ConverterVocabulary(),
#        required=False)

    isadaptive = Bool(
        title=u'Adapt to non-existent keys',
        required=True,
        default=True)
    
    def apply():
        """
        Apply all values from vocabularies
        and return object with all fields.
        """


class IMailTemplateExt(IMailTemplate):
    """ Note this schema not for persistent objects """
    
    mailfrom = TextLine(title=u'From: (email address)')
    rcpto = TextLine(title=u'To: (email address)')


class IMailTemplateAnnotable(Interface):
    """ Interface is assigned to objects which should be annotated by
    interface IMailTemplate """
    

class IMailTemplateUtilitable(Interface):
    """ This interface is appointed to objects to specify a name of the
    utility with interface IMailTemplate which they should use.  """

    mailtemplate = Choice(
        title=u'Template',
        source=UtilityVocabulary(IMailTemplate),
        required=False,
        missing_value=u'')
    
mailtemplateannotationkey = "ng.app.mailfeed.mailtemplate"