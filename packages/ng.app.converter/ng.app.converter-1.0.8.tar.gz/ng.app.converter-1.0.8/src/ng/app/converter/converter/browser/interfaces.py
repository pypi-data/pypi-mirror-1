### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertotestform interface

Interfaces for the Zope 3 based converter package

$Id: interfaces.py 52356 2009-01-15 15:53:27Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 52356 $"
 
from zope.interface import Interface
from zope.schema import Text, Bool
from zope.app.container.interfaces import IContained, IContainer

class IConverterTestForm(Interface):
    """ A converter test form object, parameters """

    text = Text(
           title=u"Text",
           description=u"Text to Parse",
           default=u"The quick brown fox jump over the lazy dog",
           required=True)

    show_source = Bool(
            title=u"Show result as source",
            description=u"Convertion result will be showed as html-source",
            default=False)
            
