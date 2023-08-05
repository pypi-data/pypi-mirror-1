### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Utility of mapperinterface names vocabulary.

$Id: mapperinteracenamevocabulary.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-15 17:16"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"
__based__   = "Sergey Shilov"

from zope.component.interface import searchInterface,interfaceToName
from zope.app.zapi import getUtilitiesFor
from zope.component.interfaces import IFactory
from zope.schema.vocabulary import SimpleVocabulary

def MapperInterfaceNameVocabulary(context):
    """Utility of mapperinterface names vocabulary"""
    
    return SimpleVocabulary.fromValues(sorted(tuple(set(
         ( interfaceToName(context, i) for i in searchInterface(None, '') )
        ))))

