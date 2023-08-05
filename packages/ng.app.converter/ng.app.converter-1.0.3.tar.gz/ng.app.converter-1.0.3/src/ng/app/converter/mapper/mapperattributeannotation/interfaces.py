### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperatributeannotation package

$Id: interfaces.py 49876 2008-02-02 14:18:55Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49876 $"

from zope.schema import Text, TextLine, Datetime, Tuple
from zope.interface import Interface

class IMapperAttributeAnnotable(Interface) :
    pass

mapperattributeannotationkey="mapperatributeannotations.mapperatributeannotations.MapperAttribute"
    