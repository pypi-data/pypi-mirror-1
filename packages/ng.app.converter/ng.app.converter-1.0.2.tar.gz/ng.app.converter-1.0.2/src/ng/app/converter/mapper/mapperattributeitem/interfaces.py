### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based mapperattributeitem package

$Id: interfaces.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Dima Khozin, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

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
