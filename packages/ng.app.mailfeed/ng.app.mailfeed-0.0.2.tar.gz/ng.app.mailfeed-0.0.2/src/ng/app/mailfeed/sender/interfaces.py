### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 53589 2009-08-14 20:10:19Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53589 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Bool, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint

#from ng.app.converter.convertervocabulary import ConverterVocabulary

from ng.lib.utilityvocabulary import UtilityVocabulary
from zope.sendmail.interfaces import IMailDelivery
                
class ISender(Interface) :
    """ Base schema for connector """

    mailfrom = TextLine(
        title=u'From',
        required=True,
        default=u'')


    delivery = Choice(
        title=u'Deivery',
        source=UtilityVocabulary(IMailDelivery),
        required=True)

    
    def send(to,msg):
        """
        Send mail using queue
        """


class ISenderAnnotable(Interface):
    """ This interface is assigned to objects which should be annotated by
    interface ISender """
    

class ISenderUtilitable(Interface):
    """Interface is assigned to objects to specify a name of the utility
    with interface ISendere which they should use. """
    
    sender = Choice(
        title=u'SMTP Sender',
        source=UtilityVocabulary(ISender),
        required=False,
        missing_value=u'')
    
senderannotationkey = "ng.app.mailfeed.sender"
