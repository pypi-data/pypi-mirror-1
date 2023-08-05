### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Converter vocabulary for the Zope 3 based converter package

$Id: convertervocabulary.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

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
