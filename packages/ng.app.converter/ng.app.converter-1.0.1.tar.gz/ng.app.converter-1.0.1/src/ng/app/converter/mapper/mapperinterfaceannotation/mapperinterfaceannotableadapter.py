### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperinterfaceannotable adapter.

$Id: mapperinterfaceannotableadapter.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"

from zope.interface import implements
from ng.app.converter.mapper.mapperinterface.mapperinterface import MapperInterface
from zope.annotation.interfaces import IAnnotations 

from interfaces import mapperinterfaceannotationkey

def MapperInterfaceAnnotableAdapter(context):
    return IAnnotations(context).setdefault(mapperinterfaceannotationkey,MapperInterface())
    