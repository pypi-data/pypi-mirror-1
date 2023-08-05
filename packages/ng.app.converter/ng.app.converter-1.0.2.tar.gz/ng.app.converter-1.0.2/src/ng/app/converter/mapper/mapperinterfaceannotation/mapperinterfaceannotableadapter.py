### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperinterfaceannotable adapter.

$Id: mapperinterfaceannotableadapter.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.interface import implements
from ng.app.converter.mapper.mapperinterface.mapperinterface import MapperInterface
from zope.annotation.interfaces import IAnnotations 

from interfaces import mapperinterfaceannotationkey

def MapperInterfaceAnnotableAdapter(context):
    return IAnnotations(context).setdefault(mapperinterfaceannotationkey,MapperInterface())
    