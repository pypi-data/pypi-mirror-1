### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The cachestore class.

$Id: cachestore.py 49862 2008-01-06 22:27:04Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49862 $"

from zope.interface import implements
from persistent import Persistent
from interfaces import ICachestore, ICachestoreContained, ICachestoreStat, ICachestoreContainer
from zope.app.container.interfaces import IContainer
from BTrees.IOBTree import IOBTree
from zope.app import zapi
from zope.app.intid.interfaces import IIntIds
from ng.app.converter.cachestoreitem.interfaces import ICachestoreItem
from zope.app.container.btree import BTreeContainer
from zope.dublincore.interfaces import IDCTimes, IZopeDublinCore
from persistent.list import PersistentList
from zope.exceptions.interfaces import DuplicationError
from zope.annotation.interfaces import IAnnotations
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.adapter.mtime.interfaces import IMTime

import time

class CacheNotValidError(Exception):
    pass

class CacheStoreItemList(PersistentList) :
    """Cache Store Item List holder"""

class CachestoreBase(object):
    """Cache store base class"""

    implements(ICachestoreContained, ICachestoreContainer, ICachestore, ICachestoreStat)
    
    #Cache time in seconds"""
    max_caching_time = 3600*24*10
    
    #Name of Intids utitity"""
    intIdsName = u''
    
    eventdelta = 2
    
    def save(self, ob, cacheStoreItem):
        """Save storeitem with object as key"""
        l = self.getCached(ob).append(cacheStoreItem)
        self.save_list(ob, l)
    
    def save_list(self, ob, cacheStoreItemList):
        """Save CacheStoreItemList with object as key"""
        try :
            self["c%016u" % zapi.getUtility(IIntIds, self.intIdsName).getId(ob)] = cacheStoreItemList
        except DuplicationError :
            del(self["c%016u" % zapi.getUtility(IIntIds, self.intIdsName).getId(ob)])
            self["c%016u" % zapi.getUtility(IIntIds, self.intIdsName).getId(ob)] = cacheStoreItemList            

    def getCached(self, ob):
        """Get CacheStoreItemList with object as key"""

        try :
            items = self["c%016u" % zapi.getUtility(IIntIds, self.intIdsName).getId(ob)]
        except KeyError :
            return CacheStoreItemList()

        l = CacheStoreItemList()
        now = time.time()
        for item in items :
            if item.converter :
                try :
                    converter = zapi.getSiteManager(self).getUtility(IConverter,item.converter)
                except LookupError,msg :
                    print "Converter",item.converter,"does not exist any more:",msg
                    return CacheStoreItemList()
                                        
                try :
                    if ((now - self.max_caching_time) < item.mtime
                        and item.mtime > (converter.mtime - self.eventdelta)
                        and item.mtime > (IMTime(ob).mtime - self.eventdelta)
                        ):
                        l.append(item)
                except TypeError,msg :
                    print "Can't define age because of",msg,"item will be reconverted"
                    l.append(item)              
        return l

    def getsave(self,ob):
        """Get cachestore with save old attributes"""
        l = get(ob)           
        self.save_list(ob, l)
        return l
     
    def regenerate_all(self) :
        """ Regenerate all objects """
        f = zapi.getUtility(IIntIds, self.intIdsName).getObject
        i = 0
        t=time.time()
        for key in list(self.keys()) :
            i+=1
            del(self[key])
            self.regenerate(f(int(key[1:])))
        return (i,time.time()-t)

    def regenerate(self, ob):
        """Regenerates Cache"""
        IPropertySheet(ob)
    
    def clean(self):
        """Cleans Cache"""
        for key in list(self.keys()) :
            del(self[key])
            
class Cachestore(CachestoreBase, BTreeContainer):
    """Cache store with BTreeContainer implementation"""
    pass
    