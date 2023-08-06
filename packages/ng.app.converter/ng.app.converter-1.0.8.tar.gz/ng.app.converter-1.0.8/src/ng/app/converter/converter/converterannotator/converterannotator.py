### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterannotator class.

$Id: converterannotator.py 50738 2008-02-19 10:46:39Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50738 $"
__date__ = "$Date: 2008-02-19 13:46:39 +0300 (Втр, 19 Фев 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements

from interfaces import IConverterAnnotator
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.converter.converter import ConverterBase

import re

class SRaiting(object):
    ''' Structure for keeping sentence raiting '''
    def __init__(self, sentence, sentence_words, words):
        self._raiting = 0
        self._sentence = sentence
        for s in sentence_words:
            if words.has_key(s): self._raiting = self._raiting + words[s]

class ConverterAnnotator(ConverterBase):
    __doc__ = IConverterAnnotator.__doc__
    
    implements(IConverterAnnotator,IConverter)
    pattern_sentences = "(?uL)(?:(?<=^)|(?<=\s))([^~=\.?!;]+[\.?!;])(?=\s|$)"
    pattern_word = "(?u)(?:(?<=\s)|(?<=\A))[^\s]+(?:(?=\s)|(?=\.)|(?=\Z))"
    _keywords = ""
    _normalisation = True
    minimalrating = 1
    
    def __init__(self, keywords, best_count = 10, normalisation = True, minimal4norm = 4):
        """ Get text and keywords as necessary parametrs. Unnecessary
        parametrs is count of sentences in annotation and use of
        normalization """
        self.best_count = best_count
        self.minimal4norm = minimal4norm
        self.normalisation = normalisation
        self.keywords = keywords

    def _getNormalisation(self) :
        return self._normalisation

    def _setNormalisation(self,normalisation) :
        self._normalisation = normalisation
        self._compile()

    normalisation = property(_getNormalisation,_setNormalisation)    

    def _getMinimal4norm(self) :
        return self._minimal4norm

    def _setMinimal4norm(self,minimal4norm) :
        self._minimal4norm = minimal4norm
        self._compile()

    minimal4norm = property(_getMinimal4norm,_setMinimal4norm)    

    def _getKeywords(self) :
        return self._keywords

    def _setKeywords(self,keywords) :
        self._keywords = keywords
        self._compile()

    keywords = property(_getKeywords,_setKeywords)    
        
    def _compile(self) :   
        keywords_split = re.findall(self.pattern_word, self.keywords)
           
        if self.normalisation == True:
            keywords_norm = [word[:(  (len(word)>=self.minimal4norm) and int(len(word)*0.8) or len(word)  )].lower() for word in keywords_split]
        else:
            keywords_norm = [word.lower() for word in keywords_split]

        self.keywords_dict = {}
        for s in keywords_norm:
            if self.keywords_dict.has_key(s):
                self.keywords_dict[s] = self.keywords_dict[s] + 1
            else:
                self.keywords_dict[s] = 1
        self._v_compile = True
            
    keywords = property(_getKeywords,_setKeywords)    
        
    def convert(self,text):
        """ Create annotation """
        text = super(ConverterAnnotator,self).convert(text)
        sentences = re.findall(self.pattern_sentences, text)
        sentences_best = []
        number = 0

        for sentence in sentences:
            words = re.findall(self.pattern_word, sentence)
            if self.normalisation == True:
                words_norm = [word[:(  (len(word)>=self.minimal4norm) and int(len(word)*0.8) or len(word)  )].lower() for word in words]
            else:
                words_norm = [word.lower() for word in words]

            sentences_best.append(SRaiting(number, words_norm, self.keywords_dict))
            number = number + 1
            
        sentences_best.sort(lambda x,y: cmp(y._raiting, x._raiting))

        sentences_best = [x for x in sentences_best if x._raiting >= self.minimalrating]
    
        sentences_best = sentences_best[:self.best_count]
        
        sentences_best.sort(
            lambda x,y: cmp(x._sentence, y._sentence) 
            )
        
        result = ""
        for a in sentences_best:
            result = result + " " + sentences[a._sentence]

        return result

if __name__ == '__main__' :
    import sys
    print ConverterAnnotator(" ".join(sys.argv[1:]),normalisation=False,best_count=3).convert(sys.stdin.read())
