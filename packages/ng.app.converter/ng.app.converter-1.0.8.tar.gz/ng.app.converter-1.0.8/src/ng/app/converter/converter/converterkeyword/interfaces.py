### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based converterkeyword package

$Id: interfaces.py 53333 2009-06-19 21:14:13Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53333 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Int, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.converter.interfaces import IConverter

class IConverterKeywordAdd(Interface) :
    keywords = Text(
        title = u'Possible keywords list',
        required=True,
        default=u""
        )
                                                                        
class IConverterKeyword(IConverter,IConverterKeywordAdd) :
    """ Select keywords from text """
