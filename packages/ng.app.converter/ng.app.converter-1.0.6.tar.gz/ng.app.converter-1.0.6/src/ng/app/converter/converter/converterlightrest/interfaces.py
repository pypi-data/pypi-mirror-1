### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterlightrest interface

Interfaces for the Zope 3 based converterlightrest package

$Id: interfaces.py 52337 2009-01-14 12:22:40Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52337 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Int, Bool
from zope.app.container.interfaces import IContained, IContainer
from ng.app.converter.converter.interfaces import IConverter

class IConverterLightReSTAdd(Interface) :
    """ A converterrest interface"""
    
    title = TextLine(
                title = u"Title",
                default=u"Converter LightReST"
                )

    use_html_filter = Bool(
                title = u"Use HTML filter",
                default = True,
                )

class IConverterLightReST(IConverter,IConverterLightReSTAdd):
    """ A converterrest interface"""