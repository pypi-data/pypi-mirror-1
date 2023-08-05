### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based converterhead package

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
                
class IConverterHead(IConverter) :
    """ A converterhead object """

    regexp = TextLine(
           title=u"Regular Expression",
           description=u"Regular expression used to find and parse some subsctring",
           default=u"(?ums)^[^:]+:\s*(?P<body>[^:]{100,2024}\.)([^:.]+:)",
           required=True)
                                                                        
    format = TextLine(
           title=u"Format Expression",
           description=u"Format expression used to generate substring based on regular expression",
           default=u"%(body)s",
           required=True)

    bytes = Int(
           title=u"Byte in header",
           description=u"Byte in header",
           default=1024,
           required=True)

    lines = Int(
           title=u"Line in header",
           description=u"Line in header",
           default=10,
           required=True)
                                                                        
