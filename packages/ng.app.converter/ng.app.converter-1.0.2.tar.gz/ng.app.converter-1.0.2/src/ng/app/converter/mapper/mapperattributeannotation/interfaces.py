### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperatributeannotation package

$Id: interfaces.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.schema import Text, TextLine, Datetime, Tuple
from zope.interface import Interface

class IMapperAttributeAnnotable(Interface) :
    pass

mapperattributeannotationkey="mapperatributeannotations.mapperatributeannotations.MapperAttribute"
    