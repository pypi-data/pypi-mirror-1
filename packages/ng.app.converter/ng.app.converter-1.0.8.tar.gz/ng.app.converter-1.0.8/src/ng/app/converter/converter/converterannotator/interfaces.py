### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterannotator interface

Interfaces for the Zope 3 based converterannotator package

$Id: interfaces.py 50717 2008-02-18 12:22:55Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50717 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Int, Bool
from zope.app.container.interfaces import IContained, IContainer
from ng.app.converter.converter.interfaces import IConverter

class IConverterAnnotatorAdd(Interface) :
    """ A converterannotator object, parameters """

    keywords = Text(
           title=u"Keywords",
           description=u"Keywords",
           default=u"",
           required=True)
    
    pattern_word = TextLine(
           title=u"Pattern Words",
           description=u"Pattern to split keyword string by keywords array.",
           default=u"(?uL)(?:(?<=\s)|(?<=\A))[^\s]+(?:(?=\s)|(?=\Z))",
           required=True)

    pattern_sentences = TextLine(
           title=u"Pattern Sentences",
           description=u"Pattern to split text onto by sentences.",
           default=u"(?uL)^\s*[^\.]+\.|\s+[^\.]+\.",
           required=True)

    # u"(?uL)(?:(?<=^)|(?<=\s))([^~=\.?!;]+[\.?!;])(?=\s|$)",

    best_count = Int(
           title=u"Count of sentences in annotation",
           description=u"Count of sentences in annotation",
           default=10,
           required=False)
	   
    normalisation = Bool(
           title=u"Creating normalisation",
           description=u"Creating normalisation",
           default=True,
           required=False)
	   
    minimal4norm = Int(
           title=u"Minimal length of word for normalisation",
           description=u"Minimal length of word for normalisation",
           default=4,
           required=False)
	   
    minimalrating = Int(
           title=u"Minimal rating",
           description=u"Minimal rating of sentences in annotation",
           default=1,
           required=False)
	   
class IConverterAnnotator(IConverter,IConverterAnnotatorAdd):
    """ A converterannotator object, parameters """

    