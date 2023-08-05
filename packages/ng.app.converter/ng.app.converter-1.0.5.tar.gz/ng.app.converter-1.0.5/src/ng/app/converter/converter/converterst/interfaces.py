### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based converterst package

$Id: interfaces.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Int, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.converter.interfaces import IConverter
                
class IConverterSTAdd(Interface) :
    """ A structured text converter object data """

    title = TextLine(title = u"Title", default=u"Converter ST")
                                                                        
class IConverterST(IConverter,IConverterSTAdd) :
    """ A structured text converter object """
    