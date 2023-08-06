### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The object2psadapter class.

$Id: object2psadapter.py 50541 2008-02-05 22:38:53Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50541 $"

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
        self.attrdict = {}
        saveNeeded = False
        cached = {}
        for (name,cache) in zapi.getUtilitiesFor(ICachestore, ob) :
            for cache in cache.getCached(ob) :
                cached[(cache.attribute,cache.converter)] = cache 

        dictinterfaces = {}
        for (mon,mo) in zapi.getUtilitiesFor(IMapperObject, ob) :
            dictinterfaces.update( mo.lookup(ob) )
         
        dictitems = dictinterfaces.items() 
        dictitems.sort(self.cmp)
        
        for iface_in, iface_outd in dictitems :
            mapattrd = iface_outd[interface.interfaceToName(self, IPropertySheet)]
            
            for attr, desc in mapattrd.items() :
                try :
                    self.attrdict[attr] = cached[(desc.attr,desc.converter)].value
                except KeyError :
                    print attr,"Конвертируем потому что кеш пуст"
                    self.attrdict[attr] = value = \
                        zapi.getSiteManager(ob) \
                            .getUtility(IConverter, desc.converter) \
                            .convert(getattr(ob, desc.attr))                
                    csi = CachestoreItem(
                        attribute=desc.attr,
                        converter=desc.converter,
                        value=value,
                        mtime=time.time())
                    cached[(desc.attr,desc.converter)] = csi
                    saveNeeded = True

        if saveNeeded :                                                
            print """ Выполняем принудительное сохранение """
            li = CacheStoreItemList()
            for value in cached.values() :
                li.append(value)

            for (name,cache) in zapi.getUtilitiesFor(ICachestore, ob) :
                cache.save_list(ob,li) 
        
class Object2PSadapter(Object2PSadapterBase):
    """ """
    implements(IPropertySheet)

    def get(self,key,default) :
        return self.attrdict.get(key,default)
	
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

        