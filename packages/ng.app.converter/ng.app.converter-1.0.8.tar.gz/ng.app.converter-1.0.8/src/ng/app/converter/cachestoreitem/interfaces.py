### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The cachestoreitem interface

Interfaces for the Zope 3 based cachestoreitem package

$Id: interfaces.py 49859 2008-01-06 21:40:27Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49859 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, List, Float
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.cachestore.interfaces import ICachestoreContainer

class ICachestoreItem(Interface):
    """ Container used as place for cached attributes """
    
    attribute 	= TextLine(
			title = u"Attribute",
			description = u"Object's attribute",
			required = True
			)

    value 	= Text(
			title = u"value",
			description = u"Converted value",
			required = True
			)

    converter 	= TextLine(
			title = u"converter",
			description = u"Converter, that used for convert attribute",
			required = True
			)

    mtime 	= Float(
			title = u"Modification time",
			description = u"Last modified time in unix format",
			required = True
			)

class ICachestoreItemContained(Interface) :
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ICachestoreContainer))
