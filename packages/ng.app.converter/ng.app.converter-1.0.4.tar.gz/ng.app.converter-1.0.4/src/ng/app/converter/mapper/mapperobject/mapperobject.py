### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperobject class.

$Id: mapperobject.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"

from zope.interface import implements
from zope.interface import providedBy
from persistent import Persistent
from interfaces import IMapperObject

from zope.app.container.contained import Contained
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IContainer
from zope.component import interface

class MapperObject(BTreeContainer):
    __doc__ = IMapperObject.__doc__
    
    implements(IMapperObject)
    

    def __setitem__(self, key, value):
        """ Check for exist key in list of all interfaces and add if exist """
        try:
            key_interface = interface.nameToInterface(self, key)
            all_interfaces = interface.searchInterface(None, '')
        except Exception,msg:
            raise ValueError, msg


        if  key_interface in all_interfaces:
            super(MapperObject, self).__setitem__(key, value)
        else: 
            raise ValueError

    def lookup(self, ob):
        all_interfaces = [interface.interfaceToName(ob,a) for a in providedBy(ob)]
        d = {}
        
        for key in all_interfaces :
            try :
                d[key] = self[key]
            except KeyError :
                pass

        return d
        
        