### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: senderannotableadapter.py 53228 2009-06-11 07:43:50Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53228 $"

from sender import SenderAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import senderannotationkey
from zope.location.location import LocationProxy 


def ISenderAnnotableAdapter(context) :

    try :
        an = IAnnotations(context)[senderannotationkey]
    except KeyError :
        an = IAnnotations(context)[senderannotationkey] = SenderAnnotation()
    return LocationProxy(an, context, "++annotations++" + senderannotationkey)
