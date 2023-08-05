### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterregexp interface

Interfaces for the Zope 3 based converterregexp package

$Id: interfaces.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field
from zope.app.container.interfaces import IContained, IContainer
from ng.app.converter.converter.interfaces import IConverter

class IConverterRegexp(IConverter):
    """ A converterregexp object """

    regexp = TextLine(
           title=u"Regular Expression",
           description=u"Regular expression used to find and parse some subsctring",
           default=u"",
           required=True)
                                                                        
    format = TextLine(
           title=u"Format Expression",
           description=u"Format expression used to generate substring based on regular expression",
           default=u"",
           required=True)
                                                                        
