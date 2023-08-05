### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The NameChooser for copies IMapperInterface.

$Id: mapperobjectnamechooser.py 49876 2008-02-02 14:18:55Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49876 $"

from zope.interface import implements
from zope.app.container.contained import NameChooser
from zope.app.container.interfaces import INameChooser
from interfaces import IMapperObjectContent

class MapperObjectNameChooser(NameChooser):
    """The NameChooser for IMapperObjectContent items"""
    implements(INameChooser)

    def chooseName(self, name, object):
        if IMapperObjectContent.providedBy(object):
            return object.name__
        else:
            return super(MapperObjectNameChooser, self).chooseName(name, object)
