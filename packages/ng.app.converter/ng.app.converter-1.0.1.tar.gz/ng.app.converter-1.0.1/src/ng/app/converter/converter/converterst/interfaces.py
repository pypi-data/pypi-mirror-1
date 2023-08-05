### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based converterst package

$Id: interfaces.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Int, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.converter.interfaces import IConverter
                
class IConverterST(IConverter) :
    """ A converterhead object """

    title = TextLine(title = u"Title", default=u"Converter ST")
                                                                        
    