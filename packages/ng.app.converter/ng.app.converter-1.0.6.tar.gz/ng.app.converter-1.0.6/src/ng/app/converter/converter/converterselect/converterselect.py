### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Converter Select class for the Zope 3 based converterselect package

$Id: converterselect.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"
__date__ = "$Date: 2008-01-03 16:40:06 +0300 (Чтв, 03 Янв 2008) $"
 
from zope.interface import implements
from interfaces import IConverterSelect
from ng.app.converter.converter.converter import ConverterBase
from ng.app.converter.converter.interfaces import IConverter
import re
                
class ConverterSelect(ConverterBase):
    __doc__ = IConverterSelect.__doc__

    implements(IConverterSelect)

    lwin = 100
    dwin = 50
    threshold = 3
    
    def __init__(self,lwin=100,dwin=50,threshold=3):
        """ Initialization the converter by regexp, bytes and lines """
        self.lwin = lwin
        self.dwin = dwin
        self.threshold = threshold

    def convert(self,text):
        """ Do convert """
        text = super(ConverterSelect,self).convert(text)        
        bt = et = 0

        queue = [0]
        seg = []        
        for c in text[0:self.lwin] :
            if c in ["<",">"] :
                queue[-1] += 1

        maxlen = 0
        maxrange = [0,0]                
        for x in range(0,len(text)-self.lwin) :
            queue.append(queue[-1])
            if text[x] in ["<",">"] :
                queue[-1]-=1
            if text[x+self.lwin] in ["<",">"] :                
                queue[-1]+=1
            queue=queue[-self.dwin:]
            if abs(queue[0]-queue[-1]) <= self.threshold and bt == 0:
                bt = x
            if abs(queue[0]-queue[-1]) > self.threshold and bt != 0 :
                
                if (self.lwin+x-(bt-self.lwin)) > maxlen :
                    maxlen = self.lwin+x-(bt-self.lwin)
                    maxrange = [bt-self.lwin,self.lwin+x]

                bt = 0                    

        bt,et = maxrange                
        return text[bt:et]
        
if __name__ == '__main__' :
    import sys
    print ConverterSelect().convert(sys.stdin.read())
    