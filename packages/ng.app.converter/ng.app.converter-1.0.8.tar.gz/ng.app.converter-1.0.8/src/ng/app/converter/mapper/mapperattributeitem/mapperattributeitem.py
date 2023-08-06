### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperattributeitem class.

$Id: mapperattributeitem.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Dima Khozin, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.interface import implements
from persistent import Persistent
from interfaces import IMapperAttributeItem
from ng.app.converter.mapper.mapperattribute.interfaces import IMapperAttributeContent
from zope.app.container.contained import Contained

class MapperAttributeItem(Persistent,Contained):
    __doc__ = IMapperAttributeItem.__doc__
    """ MapperAttributeItem object. It contains some attributes """

    implements(IMapperAttributeItem,IMapperAttributeContent)
    
    # See mapperattributeitem.interfaces.IMapperAttributeItem
    attr = None

    # See mapperattributeitem.interfaces.IMapperAttributeItem
    converter = None
    
