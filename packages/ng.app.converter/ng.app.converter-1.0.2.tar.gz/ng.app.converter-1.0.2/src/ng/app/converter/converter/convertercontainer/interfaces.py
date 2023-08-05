### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterchain interface

Interfaces for the Zope 3 based converterchain package

$Id: interfaces.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Arvid, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Field
from zope.app.container.interfaces import IContained, IContainer

from zope.app.container.ordered import IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition

from ng.app.converter.converter.interfaces import IConverter

class IConverterContainer(IOrderedContainer,IConverter):
    """ A convertercontainer object """
    
    def __setitem__(name, object):
        """Add converter"""
    __setitem__.precondition = ItemTypePrecondition(IConverter)

