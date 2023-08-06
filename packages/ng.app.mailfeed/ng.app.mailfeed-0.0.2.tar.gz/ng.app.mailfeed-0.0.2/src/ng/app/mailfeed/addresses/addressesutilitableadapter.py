### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: addressesutilitableadapter.py 53262 2009-06-12 11:36:18Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53262 $"

from zope.app.zapi import getUtility
from addresses import Addresses
from interfaces import IAddresses,IAddressesUtilitable

def IAddressesUtilitableAdapter(context) :
    return getUtility(IAddresses,context=context,name=IAddressesUtilitable(context).addresses)
    