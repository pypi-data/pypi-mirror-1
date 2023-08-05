### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperattribute class.

$Id: mapperattribute.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Dima Khozin, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"
__date__ = "$Date: 2008-02-06 23:22:05 +0300 (Срд, 06 Фев 2008) $"
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

