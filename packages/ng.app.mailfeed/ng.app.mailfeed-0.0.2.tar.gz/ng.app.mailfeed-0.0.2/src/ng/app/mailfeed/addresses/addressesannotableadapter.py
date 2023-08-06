### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: addressesannotableadapter.py 53228 2009-06-11 07:43:50Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"

from addresses import AddressesAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import addressesannotationkey
from zope.location.location import LocationProxy 


def IAddressesAnnotableAdapter(context) :

    try :
        an = IAnnotations(context)[addressesannotationkey]
    except KeyError :
        an = IAnnotations(context)[addressesannotationkey] = AddressesAnnotation()
    return LocationProxy(an, context, "++annotations++" + addressesannotationkey)
