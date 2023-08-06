### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 53228 2009-06-11 07:43:50Z cray $
"""
__author__  = "Ilshad Habibullin, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"
 
from zope.interface import Interface
from zope.schema import TextLine,  Bool, Datetime, Object, Tuple, Choice
from ng.lib.utilityvocabulary import UtilityVocabulary


class IAddress(Interface) :
    """ An address """

    name = TextLine(
        title=u'Name', required=False)

    address = TextLine(
        title=u'Address', default=u'',  required=True)

    registered = Datetime(
        title=u'Registration data', required=False)

    isactive = Bool(
        title=u'Active address', default=True, required=True)


class IAddresses(Interface):
    """ Storage for addresses """

    addresses = Tuple(
        title = u'Addresses',
        required = False,
        value_type = Object(title = u'Address',
                            schema = IAddress))

    def values():
        """ Return tuple of tuples (name, address) when isactive=True.  """

class IAddressesAnnotable(Interface):
    """
    Marker for objects which is can use
    adapters to IAddressesAnnotation.
    """

class IAddressesUtilitable(Interface):
    """ """
    addresses = Choice(
        title=u'Address list source',
        source=UtilityVocabulary(IAddresses),
        required=False,
        missing_value=u'')

class IAddressesUtility(IAddresses):
    """ """
    
class IAddressesAnnotation(IAddresses):
    """ """

addressesannotationkey = "ng.app.mailfeed.addresses"
