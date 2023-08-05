### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterrest interface

Interfaces for the Zope 3 based converterrest package

$Id: interfaces.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Int
from zope.app.container.interfaces import IContained, IContainer
from ng.app.converter.converter.interfaces import IConverter

class IConverterReSTAdd(Interface) :
    """ A converterrest interface"""
    
    title = TextLine(
                title = u"Title",
                default=u"Converter ReST"
                )

    input_encoding = TextLine(
                title = u"Input Encoding",
                default=u"unicode"
                )

    output_encoding = TextLine(
                title = u"Output Encoding",
                default=u"unicode"
                )

    initial_header_level = Int(
                title = u"Initial Header Level",
                default = 3
                )
                
    halt_level = Int(
                title = u"Halt Level",
                default = 6
                )

class IConverterReST(IConverter,IConverterReSTAdd):
    """ A converterrest interface"""