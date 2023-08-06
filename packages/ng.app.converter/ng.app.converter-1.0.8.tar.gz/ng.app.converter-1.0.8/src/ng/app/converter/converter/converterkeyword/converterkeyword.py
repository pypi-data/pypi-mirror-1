### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ConverterKeyword class for the Zope 3 based converterhead package

$Id: converterkeyword.py 53337 2009-06-20 08:03:42Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53337 $"
                    
 
from zope.interface import implements
from interfaces import IConverterKeyword
from ng.app.converter.converter.converter import ConverterBase
from ng.app.converter.converter.interfaces import IConverter
import re
                
class ConverterKeyword(ConverterBase):
    __doc__ = IConverterKeyword.__doc__

    implements(IConverterKeyword,IConverter)
    
    keywords = ""

    def __init__(self, keywords=u""):
        """ Initialization the converter by regexp, bytes and lines """
        self.keywords = keywords

    def convert(self,text):
        """ Select expected keywords from text """
        text = unicode(super(ConverterKeyword,self).convert(text).lower())
        return ", ".join(sorted(
            self.convert_keywords(text) 
            ))
        
    def convert_keywords(self,text) :
        d = {}
        subjects = []
        for subject in [ [0,0,x.strip()] for x in self.keywords.lower().split("\n") if x.strip()] :
            subjects.append(subject)

            try :
                subject[2],keywords = [x.strip() for x in subject[2].split(":")]
            except ValueError :
                keywords = [len(x) >= 8 and x[:-3] or x for x in subject[2].split() if len(x) > 3]
            else :
                keywords = [ x for x in keywords.split() if x ]

            for keyword in set(keywords):
                subject[1] += 1
                d.setdefault(keyword,[]).append(subject)
                
        for keyword in d :
            if keyword in text :
                for subject in d[keyword] :
                    subject[0] += 1
                    
        return [ x[2] for x in subjects if x[0] >= x[1]]
            
                
        
        
        
    def convert_full(self,text) :        
        dphs = dict([ (tuple([ (len(x) >= 8) and x[:-3] or x for x in y.split()]),y) for y in [ x.strip() for x in self.keywords.lower().split("\n") ] ])

        tokens = re.compile(u"\w+",re.U).findall(text)
        queue = tokens[0:5]
        keywords = []
        for token in tokens[5:] + [""]*5:
            queue.append(token)
            
            for key, value in dphs.items() :
                weight = 0
                for a,v in zip(key,queue) :
                    if len(a) > 3 and a == v[0:len(a)] :
                        weight += 1
                if weight > 0 :
                    keywords.append(value)
                    del dphs[key]    
                    if not dphs :
                        break
                   
            del queue[0]                
        
        return keywords 
        
if __name__ == '__main__' :
    import sys
    print ConverterKeyword(unicode("\n".join(sys.argv[1:]))).convert(unicode(sys.stdin.read()))
    