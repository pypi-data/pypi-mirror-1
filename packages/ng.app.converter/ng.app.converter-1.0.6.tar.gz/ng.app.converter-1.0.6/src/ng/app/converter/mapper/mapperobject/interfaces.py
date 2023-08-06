### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperobject package

$Id: interfaces.py 49774 2008-01-03 13:50:48Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49774 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field
from zope.app.container.interfaces import IContained, IContainer, IContainerNamesContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.mapper.mapperinterface.interfaces import IMapperInterface

class IMapperObject(IContainerNamesContainer):
    """ A mapperobject interface """

    def __setitem__(name, value):
        pass
    
    __setitem__.precondition = ItemTypePrecondition(IMapperInterface)



class IMapperObjectContent(IContained):
    """Interface that specifies the type of objects that can contain
    mapper interfaces."""

    __parent__ = Field(
        constraint = ContainerTypesConstraint(IMapperObject))

