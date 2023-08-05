### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperattributeitem package

$Id: interfaces.py 49876 2008-02-02 14:18:55Z cray $
"""
__author__  = "Dima Khozin, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49876 $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice
from zope.app.container.interfaces import IContained, IContainer
from ng.app.converter.convertervocabulary import ConverterVocabulary

class IMapperAttributeItem(Interface):
    """ A mapperattributeitem interface """
    converter = Choice (
        title=u"our converter",
        description=u"name of converter",
        required=True,
        source=ConverterVocabulary()
	)
    
    attr = TextLine (
        title=u"some attribute",
        description=u"some descr",
        default=u"",
        required=False)
