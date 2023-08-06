### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperinterfaceannotation products.

$Id: interfaces.py 49774 2008-01-03 13:50:48Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49774 $"

from zope.interface import Interface

class IMapperInterfaceAnnotable(Interface) :
    pass

mapperinterfaceannotationkey="mapperinterfaceannotation.mapperinterfaceannotation.MapperInterface"
    