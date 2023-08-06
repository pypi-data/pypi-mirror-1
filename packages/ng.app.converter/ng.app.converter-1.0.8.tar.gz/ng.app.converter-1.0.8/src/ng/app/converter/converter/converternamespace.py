# -*- coding: utf-8 -*-
"""The converter namespace adapter.

$Id: converternamespace.py 53286 2009-06-14 13:01:00Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53286 $"

from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import SimpleHandler
from zope.app.zapi import getUtility, getMultiAdapter
from ng.app.converter.converter.interfaces import IConverter

class ConverterNamespace(SimpleHandler):
    """ ++converter++ """

    implements(ITraversable)

    def traverse(self,name,ignored) :
        """ Get registered converter by name """
        
        return getUtility(IConverter,context=self.context,name=name)


