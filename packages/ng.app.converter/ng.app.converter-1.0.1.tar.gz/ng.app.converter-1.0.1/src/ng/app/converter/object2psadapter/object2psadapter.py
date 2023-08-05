### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The object2psadapter class.

$Id: object2psadapter.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"

from zope.interface import implements
from interfaces import IPropertySheet, IAttributeConvertable

from zope.component import interface
from ng.app.converter.cachestore.cachestore import CacheStoreItemList
from ng.app.converter.cachestore.interfaces import ICachestore
from ng.app.converter.cachestoreitem.cachestoreitem import CachestoreItem

from ng.app.converter.mapper.mapperobject.mapperobject import MapperObject
from ng.app.converter.mapper.mapperobject.interfaces import IMapperObject
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.mapper.mapperattribute.interfaces import IMapperAttribute
from zope.app import zapi
import time

class Object2PSadapterBase(object):
    """ Base class Object2PSadapter with all logic """

    implements(IPropertySheet)

    __used_for__ = IAttributeConvertable
    
    def cmp(self,(nx,ox),(ny,oy)) :
        x = interface.nameToInterface(self,nx)
        y = interface.nameToInterface(self,ny)
        if issubclass(x,y) :
            return 1
        elif issubclass(y,x) :
            return -1
        return cmp(nx,ny)
        
    def __init__(self, ob):
        print "1001"
        self.attrdict = {}
        successCached = False
        cached = {}
        print "1001-2"
        for (name,cache) in zapi.getUtilitiesFor(ICachestore, ob) :
            print "1001-3",name,cache
            for cache in cache.getCached(ob) :
                print "1001-4",cache
                cached[(cache.attribute,cache.converter)] = cache 
        print "1002"

        dictinterfaces = {}
        for (mon,mo) in zapi.getUtilitiesFor(IMapperObject, ob) :
            dictinterfaces.update( mo.lookup(ob) )
         
        print "1003"
        dictitems = dictinterfaces.items() 
        dictitems.sort(self.cmp)
        print "1013"
        for iface_in, iface_outd in dictitems :
            print "1014"
            mapattrd = iface_outd[interface.interfaceToName(self, IPropertySheet)]
            print "1015"
            
            for attr, desc in mapattrd.items() :
                print "1016"
                
                try :
                    self.attrdict[attr] = cached[(desc.attr,desc.converter)].value
                    print "1018"
                    
                except KeyError :
                    print "1017",desc.converter,desc.attr
                    self.attrdict[attr] = value = \
                        zapi.getSiteManager(ob) \
                            .getUtility(IConverter, desc.converter) \
                            .convert(getattr(ob, desc.attr))                
                    print "1022"                            
                    csi = CachestoreItem(
                        attribute=desc.attr,
                        converter=desc.converter,
                        value=value,
                        mtime=time.time())
                    print "1023"                        
                    cached[(desc.attr,desc.converter)] = csi
                print "1019"
                                    
        li = CacheStoreItemList()
        print "1020"
        for value in cached.values() :
            print "1021"
            li.append(value)
        print "1004"

        for (name,cache) in zapi.getUtilitiesFor(ICachestore, ob) :
            cache.save_list(ob,li) 
        print "1005"
        
class Object2PSadapter(Object2PSadapterBase):
    """ """
    implements(IPropertySheet)
	
    def __getitem__(self, key):
        return self.attrdict[key]

    def keys(self) :
        return self.attrdict.keys()

    def items(self) :
        return self.attrdict.items()

    def values(self) :
        return self.attrdict.values()

    def __str__(self) :
        return self.attrdict.__str__()

        