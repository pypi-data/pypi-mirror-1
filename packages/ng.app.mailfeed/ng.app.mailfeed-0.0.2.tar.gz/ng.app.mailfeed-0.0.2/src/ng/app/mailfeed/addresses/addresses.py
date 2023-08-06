### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: addresses.py 53228 2009-06-11 07:43:50Z cray $
"""

__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"

from persistent import Persistent
from zope.interface import Interface, implements
from zope.app.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

from interfaces import IAddress, IAddresses
from interfaces import IAddressesUtility, IAddressesAnnotation


class Address(object) :

    implements(IAddress)

    name = ''
    address = ''
    registered = ''
    isactive = True

class AddressesBase(object):
    implements(IAddresses)
    """ Abstract class """

    def __init__(self):
        self.addresses = []

    def values(self):
        return [(addr.name, addr.address)
                for addr in self.addresses
                if addr.isactive]

class Addresses(AddressesBase, Contained, Persistent):
    """ Content class """

class AddressesAnnotation(AddressesBase, Persistent):
    """ Annotation """
