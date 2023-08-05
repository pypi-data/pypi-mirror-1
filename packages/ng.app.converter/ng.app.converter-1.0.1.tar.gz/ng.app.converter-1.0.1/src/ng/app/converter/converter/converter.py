### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The base converter class.

$Id: converter.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"

from zope.interface import implements
from interfaces import IConverter,IConverterContained
from persistent import Persistent
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.contained import Contained
from ng.adapter.mtime.interfaces import IMTime

class ConverterBase(Persistent,Contained):
    __doc__ = IConverter.__doc__

    implements(IConverter,IConverterContained)
    
    def convert(self,s) :
        if s is None :
            s = u""
        return s

    @property
    def mtime(self) :
        return IMTime(self).mtime
        