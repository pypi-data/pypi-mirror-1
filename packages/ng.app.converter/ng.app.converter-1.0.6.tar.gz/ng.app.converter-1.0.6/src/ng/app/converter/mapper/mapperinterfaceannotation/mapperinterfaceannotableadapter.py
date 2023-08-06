### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperinterfaceannotable adapter.

$Id: mapperinterfaceannotableadapter.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.interface import implements
from ng.app.converter.mapper.mapperinterface.mapperinterface import MapperInterface
from zope.annotation.interfaces import IAnnotations 

from interfaces import mapperinterfaceannotationkey

def MapperInterfaceAnnotableAdapter(context):
    return IAnnotations(context).setdefault(mapperinterfaceannotationkey,MapperInterface())
    