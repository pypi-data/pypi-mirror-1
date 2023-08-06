### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Converter vocabulary for the Zope 3 based converter package

$Id: convertervocabulary.py 49830 2008-01-06 03:47:59Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49830 $"

from zope.interface import implements, alsoProvides
from zope.schema.vocabulary import SimpleVocabulary
from ng.app.converter.converter.interfaces import IConverter
from zope.schema.interfaces import  IContextSourceBinder, ITextLine
from zope.app.zapi import getUtilitiesFor

class ConverterVocabulary(object) :
    implements(IContextSourceBinder)
        
    def __call__(self, ob) :
        vocabulary = SimpleVocabulary.fromValues(
            sorted([ x for x,y in getUtilitiesFor(IConverter,context=ob)])
        )
        alsoProvides(vocabulary,ITextLine)
        return vocabulary
