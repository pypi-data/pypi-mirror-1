### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ConverterHead class for the Zope 3 based converterhead package

$Id: converterhead.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"
                    
 
from zope.interface import implements
from interfaces import IConverterHead
from ng.app.converter.converter.converter import ConverterBase
from ng.app.converter.converter.interfaces import IConverter
import re
                
class ConverterHead(ConverterBase):
    __doc__ = IConverterHead.__doc__

    implements(IConverterHead,IConverter)
    
    def __init__(self, regexp="", format="", bytes=1024, lines=8):
        """ Initialization the converter by regexp, bytes and lines """
        self.regexp = regexp
        self.format = format
        self.bytes = bytes
        self.lines = lines

    def convert(self,text):
        """ Do guillotine """
        text = super(ConverterHead,self).convert(text)
        text = "\n".join(text[0:self.bytes].split("\n")[0:self.lines])

        res = re.compile(self.regexp).search(text)        
        if res :
            return self.format % res.groupdict() 

        return ""
        
if __name__ == '__main__' :
    import sys
    print ConverterHead(regexp=sys.argv[1],format=sys.argv[2],bytes=int(sys.argv[3]),lines=int(sys.argv[4])).convert(sys.stdin.read())
    