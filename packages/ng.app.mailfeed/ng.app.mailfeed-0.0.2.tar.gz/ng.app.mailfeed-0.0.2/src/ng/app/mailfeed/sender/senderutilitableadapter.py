### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: senderutilitableadapter.py 53228 2009-06-11 07:43:50Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"

from zope.app.zapi import getUtility
from sender import Sender
from interfaces import ISender, ISenderUtilitable

def ISenderUtilitableAdapter(context) :
    return getUtility(ISender,context=context,name=ISenderUtilitable(context).sender)
    