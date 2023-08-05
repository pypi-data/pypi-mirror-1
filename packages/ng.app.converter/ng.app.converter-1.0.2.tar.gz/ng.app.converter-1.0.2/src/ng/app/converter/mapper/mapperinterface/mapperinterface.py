### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperinterface class.

$Id: mapperinterface.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.interface import implements
from persistent import Persistent
from zope.app.container.btree import BTreeContainer
from interfaces import IMapperInterface,IMapperInterfaceSchema
from ng.app.converter.mapper.mapperobject.interfaces import IMapperObjectContent

class MapperInterface(BTreeContainer):
    """Mapper interface Container Class"""

    implements(IMapperInterfaceSchema,IMapperObjectContent)    
