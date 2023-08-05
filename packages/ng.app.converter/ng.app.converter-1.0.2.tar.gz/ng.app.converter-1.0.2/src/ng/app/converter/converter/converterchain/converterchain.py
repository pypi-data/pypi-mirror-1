### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ConverterChain class for the Zope 3 based convertercall package

$Id: converterchain.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.interface import implements,implementedBy
from interfaces import IConverterChain
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.converter.converter import ConverterBase
import re
from zope.app.zapi import getUtility

class ConverterChain(ConverterBase):
    __doc__ = IConverterChain.__doc__

    implements(IConverterChain)

    iftype="ifall"
    ifcondition = u""
    doforeach = False
    chain = ()
    
    def ifall(self,text) :
        return True
        
    def ifempty(self,text) :
        return not bool(text)
        
    def ifregexp(self,text) :
        return bool(re.compile(self.ifcondition).search(text))

    def ifnotregexp(self,text) :
        return not bool(re.compile(self.ifcondition).search(text))
        
    def __init__(self):
        super(ConverterChain, self).__init__()
 
    def convert(self,text):
        text = super(ConverterChain,self).convert(text)
        if getattr(self,self.iftype)(text) :
            for name in self.chain :
                text = getUtility(IConverter,context=self,name=name).convert(text) 
                if self.doforeach and getattr(self,self.iftype)(text) :
                    break
                    
        return text

    @property
    def mtime(self) :
        return max(super(ConverterChain,self).mtime,
            max([ getUtility(IConverter,context=self,name=x).mtime for x in self.chain ])
            )