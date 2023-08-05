### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperatributeannotation package

$Id: interfaces.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"

from zope.schema import Text, TextLine, Datetime, Tuple
from zope.interface import Interface

class IMapperAttributeAnnotable(Interface) :
    pass

mapperattributeannotationkey="mapperatributeannotations.mapperatributeannotations.MapperAttribute"
    