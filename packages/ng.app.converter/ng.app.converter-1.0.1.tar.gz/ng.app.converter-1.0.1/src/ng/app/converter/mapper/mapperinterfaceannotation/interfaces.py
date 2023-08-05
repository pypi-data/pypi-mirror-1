### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperinterfaceannotation products.

$Id: interfaces.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"

from zope.interface import Interface

class IMapperInterfaceAnnotable(Interface) :
    pass

mapperinterfaceannotationkey="mapperinterfaceannotation.mapperinterfaceannotation.MapperInterface"
    