### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperatributeannotation package

$Id: interfaces.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"

from zope.schema import Text, TextLine, Datetime, Tuple
from zope.interface import Interface

class IMapperAttributeAnnotable(Interface) :
    pass

mapperattributeannotationkey="mapperatributeannotations.mapperatributeannotations.MapperAttribute"
    