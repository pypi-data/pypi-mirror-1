### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertotestform interface

Interfaces for the Zope 3 based converter package

$Id: interfaces.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"
 
from zope.interface import Interface
from zope.schema import Text
from zope.app.container.interfaces import IContained, IContainer

class IConverterTestForm(Interface):
    """ A converter test form object, parameters """

    text = Text(
           title=u"Text",
           description=u"Text to Parse",
           default=u"Brown fox skip over lazy dog",
           required=True)

