### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperinterfaceannotation products.

$Id: interfaces.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"

from zope.interface import Interface

class IMapperInterfaceAnnotable(Interface) :
    pass

mapperinterfaceannotationkey="mapperinterfaceannotation.mapperinterfaceannotation.MapperInterface"
    