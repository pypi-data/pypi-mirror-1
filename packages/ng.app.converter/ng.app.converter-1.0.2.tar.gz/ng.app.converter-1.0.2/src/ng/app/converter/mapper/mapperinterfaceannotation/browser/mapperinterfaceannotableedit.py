### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MapperInterfaceAnnotable edit mixin

$Id: mapperinterfaceannotableedit.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.schema import getFieldNames 
from ng.app.converter.mapper.mapperinterface.interfaces import IMapperInterface

class MapperInterfaceAnnotableEdit(object) :
    def getData(self,*kv,**kw) :
        self.na = IMapperInterface(self.context)
        return [ (x,getattr(self.na,x)) for x in  getFieldNames(IMapperInterface)]

    def setData(self,d,**kw) :
        for x in getFieldNames(IMapperInterface) :
            setattr(self.na,x,d[x])
        return True
        
