### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterlightrest interface

Interfaces for the Zope 3 based converterlightrest package

$Id: interfaces.py 53400 2009-07-09 21:35:48Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53400 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Int, Bool
from zope.app.container.interfaces import IContained, IContainer
from ng.app.converter.converter.interfaces import IConverter

class IConverterDictProxyAdd(Interface) :
    """ A converterrest interface"""
    
    title = TextLine(
                title = u"Title",
                default=u"Converter DictProxy"
                )

    prefix = TextLine(
                title = u"Prefix",
                default = u"/@@proxy",
                )

class IConverterDictProxy(IConverter,IConverterDictProxyAdd):
    """ A converterrest interface"""