### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperinterfaceannotation products.

$Id: interfaces.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"

from zope.interface import Interface

class IMapperInterfaceAnnotable(Interface) :
    pass

mapperinterfaceannotationkey="mapperinterfaceannotation.mapperinterfaceannotation.MapperInterface"
    