### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based convertercall package

$Id: interfaces.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"
 
from zope.interface import implements, Interface, alsoProvides
from zope.schema import Text, TextLine, Field, Bool, Datetime, Choice, Tuple
from zope.schema.interfaces import ITextLine
                
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.convertervocabulary import ConverterVocabulary
from zope.schema.vocabulary import SimpleVocabulary


class IConverterChain(IConverter):
    """ A convertercall object """

    iftype = Choice(title=u'Condition Type',
        vocabulary = SimpleVocabulary.fromValues(['ifall','ifempty','ifregexp','ifnotregexp']),
        default='ifall'
        )
        
    ifcondition = TextLine(title=u'condition', default=u'', required=False)        
    
    doforeach = Bool(
        title=u'Check for each', 
        description = u'Check condition for each converter',
        default=False
        )
        
    chain = Tuple(
        title=u'Converters',
        description=u'Chain of converters called by converter',
        value_type=Choice(
            title=u'Converter',
            source = ConverterVocabulary()
            )
        )
        
