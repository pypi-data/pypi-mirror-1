### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperattribute package

$Id: interfaces.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Dima Khozin, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ContainerTypesConstraint, ItemTypePrecondition
from ng.app.converter.mapper.mapperattributeitem.interfaces import IMapperAttributeItem

class IMapperAttribute(IContainer):
    """ IMapperAttribute can contain IMapperAttributeItem """
    def __setitem__(name, object):
        """ add imapperattributeitem object """

    __setitem__.precondition = ItemTypePrecondition(IMapperAttributeItem)

class IMapperAttributeSchema(IMapperAttribute):
    """Additional interface to create schema for adding and edditing"""
    
    name__ = Choice(
        title=u'Content name',
        description=u'Name class for resource',
        vocabulary='MapperInterfaceName',
        required=True)


class IMapperAttributeContent(IContained):
    """Interface that specifies the type of objects that can contain
    mapper interfaces."""

    __parent__ = Field(
        constraint = ContainerTypesConstraint(IMapperAttribute))

