### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperatributeannotation package

$Id: interfaces.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"

from zope.schema import Text, TextLine, Datetime, Tuple
from zope.interface import Interface

class IMapperAttributeAnnotable(Interface) :
    pass

mapperattributeannotationkey="mapperatributeannotations.mapperatributeannotations.MapperAttribute"
    