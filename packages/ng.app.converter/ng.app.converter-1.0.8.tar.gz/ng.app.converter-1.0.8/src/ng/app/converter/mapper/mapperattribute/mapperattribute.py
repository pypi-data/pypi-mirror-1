### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperattribute class.

$Id: mapperattribute.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Dima Khozin, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"
__date__ = "$Date: 2008-01-03 16:40:06 +0300 (Чтв, 03 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements
from interfaces import IMapperAttributeSchema,IMapperAttribute
from zope.app.container.btree import BTreeContainer
from ng.app.converter.mapper.mapperinterface.interfaces import IMapperInterfaceContent

class MapperAttribute(BTreeContainer):
    __doc__ = IMapperAttribute.__doc__
    """ container for MapperAttributesItem """

    name__ = ""
    implements(IMapperAttributeSchema,IMapperInterfaceContent)

