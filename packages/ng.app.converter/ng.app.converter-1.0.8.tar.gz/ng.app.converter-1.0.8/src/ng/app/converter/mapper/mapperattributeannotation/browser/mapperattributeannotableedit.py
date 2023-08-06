### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MapperAttributeAnnotable edit mixin for MapperAttribute

$Id: mapperattributeannotableedit.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.schema import getFieldNames 
from ng.app.converter.mapper.mapperattribute.interfaces import IMapperAttribute

class MapperAttributeAnnotableEdit(object) :
    def getData(self,*kv,**kw) :
        self.na = IMapperAttribute(self.context)
        return [ (x,getattr(self.na,x)) for x in  getFieldNames(IMapperAttribute)]

    def setData(self,d,**kw) :
        for x in getFieldNames(IMapperAttribute) :
            setattr(self.na,x,d[x])
        return True
        
