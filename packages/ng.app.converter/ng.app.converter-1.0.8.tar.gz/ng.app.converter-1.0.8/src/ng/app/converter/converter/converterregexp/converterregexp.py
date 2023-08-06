### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterregexp class.

$Id: converterregexp.py 52439 2009-02-01 11:37:53Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52439 $"

from zope.interface import implements
from interfaces import IConverterRegexp
from ng.app.converter.converter.converter import ConverterBase
from ng.app.converter.converter.interfaces import IConverter
import re
from urllib import quote

class EDict(object) :
    d = {}
    def __init__(self,d={},**kw) :
        self.d = {}
        self.d = dict([ (str(x),y) for x,y in d.items()] )
        self.d['quote'] = lambda x : quote(str(x))
            

    def __getitem__(self,name) :
        try :
            return self.d[name]
        except KeyError :
            return eval(str(name), globals(), self.d)

        try :
            pass
        except Exception, msg :
            raise KeyError, str(msg)

class ConverterRegexp(ConverterBase):
    __doc__ = IConverterRegexp.__doc__

    implements(IConverterRegexp,IConverter)
    
    def __init__(self, regexp="", format=""):
        """ Initialization converter by regexp and format parameter """
        self.regexp = regexp
        self.format = format

    def convert(self,text):
        """ Do substitution """
        text = super(ConverterRegexp,self).convert(text)
        if text is None :
            return ""

        return \
            re.compile(self.regexp).sub(
                lambda x : self.format  % EDict(x.groupdict()) ,
                text )

if __name__ == '__main__' :
    import sys
    print ConverterRegexp(regexp=sys.argv[1],format=sys.argv[2]).convert(sys.stdin.read())
