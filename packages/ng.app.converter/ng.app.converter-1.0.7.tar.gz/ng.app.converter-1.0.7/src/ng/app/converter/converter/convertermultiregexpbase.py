
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MultiRegexpBase class for the Zope 3 based ng.app.converter package

$Id: convertermultiregexpbase.py 52439 2009-02-01 11:37:53Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52439 $"

from ng.app.converter.converter.converter import ConverterBase
import re

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


class ConverterMultiRegexpBase(ConverterBase) :
    """ Базовый класс для объектно-ориентированной библиотеки конвертеров
    """

    def convert(self, text) :
        """ Метод, производящий конвертирование
        """
        res = super(ConverterMultiRegexpBase, self).convert(text)
        
        attrs = sorted( [ x for x in dir(self) if x.startswith("_rule_") ] )
                
        for rule in (y for y in (getattr(self,x) for x in attrs) if y):
            res = re.compile(rule[0]).sub(
                  lambda x : rule[1] % EDict(x.groupdict()),
                  res)

        return res


if __name__ == '__main__' :
    
    import sys
    
    rules = [(sys.argv[i], sys.argv[i + 1]) for i in range (1, len(sys.argv) - 1, 2) ]
    
    d = {}

    for i in range(len(rules)):
        d[u'__rule_%02d__' % i] = rules[i]

    TestMultiRegexp = type('TestMultiRegexp',
                           (ConverterMultiRegexpBase,),
                           d)
    
    tcb = TestMultiRegexp()
    print tcb.convert(sys.stdin.read()).replace("\\n","\n")
