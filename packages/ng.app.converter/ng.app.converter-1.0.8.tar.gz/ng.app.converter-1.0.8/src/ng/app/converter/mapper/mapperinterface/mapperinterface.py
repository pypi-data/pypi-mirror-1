### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperinterface class.

$Id: mapperinterface.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.interface import implements
from persistent import Persistent
from zope.app.container.btree import BTreeContainer
from interfaces import IMapperInterface,IMapperInterfaceSchema
from ng.app.converter.mapper.mapperobject.interfaces import IMapperObjectContent

class MapperInterface(BTreeContainer):
    """Mapper interface Container Class"""

    implements(IMapperInterfaceSchema,IMapperObjectContent)    
