### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperinterface package

$Id: interfaces.py 49774 2008-01-03 13:50:48Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49774 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice
from zope.app.container.interfaces import IContained, IContainer, IContainerNamesContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.mapper.mapperattribute.interfaces import IMapperAttribute

class IMapperInterface(IContainerNamesContainer):
    """Mapper interface"""
    
    def __setitem__(name, value):
        pass
    
    __setitem__.precondition = ItemTypePrecondition(IMapperAttribute)

class IMapperInterfaceSchema(IMapperInterface):
    """Additional interface to create schema for adding and edditing"""
    
    name__ = Choice(
        title=u'Content name',
        description=u'Name class for resource',
        vocabulary='MapperInterfaceName',
        required=True)




class IMapperInterfaceContent(IContained):
    """Interface that specifies the type of objects that can contain
    mapper interfaces."""

    __parent__ = Field(
        constraint = ContainerTypesConstraint(IMapperInterface))


