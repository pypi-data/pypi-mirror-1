### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterchain class.

$Id: convertercontainer.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"
__date__    = "$Date: 2008-02-06 23:22:05 +0300 (Срд, 06 Фев 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements
from interfaces import IConverterContainer
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.converter.converter import ConverterBase

from zope.app.container.ordered import OrderedContainer
from zope.app.container.ordered import IOrderedContainer

import copy

class ConverterContainer(ConverterBase, OrderedContainer):
    __doc__ = IConverterContainer.__doc__

    implements(IConverterContainer)
    
    def __init__(self):
        super(ConverterContainer, self).__init__()
 
    def keys(self):
        res = sorted( super(ConverterContainer, self).keys() )
        self.updateOrder(res)
        return res
    
    def items(self):
        self.keys()
        return super(ConverterContainer, self).items()

    def __setitem__(self, name, object):
        super(ConverterContainer, self).__setitem__(name, object)
        self.keys()
    
    def convert(self,text):
        text = super(ConverterContainer,self).convert(text)
        for converter in self.values() :
            text = converter.convert(text) 
        return text

    @property
    def mtime(self) :
        return max(super(ConverterContainer,self).mtime,
            max([ IConverter(x).mtime for x in self.values() ])
            )
 

