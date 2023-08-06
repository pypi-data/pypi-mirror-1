### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The NameChooser for copies IMapperInterface.

$Id: mapperattributenamechooser.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Andrey Orlov,2007"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"
__based__ = "Sergey Shilov"

from zope.interface import implements
from zope.app.container.interfaces import INameChooser
from ng.adapter.namechooser.namechooser import NameChooser
from interfaces import IMapperAttributeContent, IMapperAttributeItem

class MapperAttributeNameChooser(NameChooser):
    """The NameChooser for IMapperAttribute content items"""
    implements(INameChooser)

    def chooseName(self, name, object):
        return super(MapperAttributeNameChooser,self).chooseName(
            name or IMapperAttributeItem(object).attr, object
            )

