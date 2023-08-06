### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Custom widget for complex addresses form 

$Id: widgets.py 53588 2009-08-13 21:12:31Z cray $
"""
__author__  = "Ilshad Habibullin, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53588 $"


from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget
from ng.app.mailfeed.addresses.addresses import Address


AddressesTupleWidget = CustomWidgetFactory(
    TupleSequenceWidget,
    subwidget = CustomWidgetFactory(
        ObjectWidget,
        Address))

