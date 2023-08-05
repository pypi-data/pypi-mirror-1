### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based converterselect package

$Id: interfaces.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Int, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.converter.interfaces import IConverter
                
class IConverterSelectAdd(Interface) :
    """ A converterselect object data """

    title = TextLine(title = u"Title", default=u"Converter Select")
                                                                        
    lwin = Int(title=u"Window length",default=100,required=True);    

    dwin = Int(title=u"Window delta",default=50,required=True);    

    threshold = Int(title=u"Threshold",default=3,required=True);    

class IConverterSelect(IConverter,IConverterSelectAdd) :
    """ A converterselect object """
    