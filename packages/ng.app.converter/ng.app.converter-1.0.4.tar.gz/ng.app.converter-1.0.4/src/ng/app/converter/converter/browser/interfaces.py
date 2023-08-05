### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertotestform interface

Interfaces for the Zope 3 based converter package

$Id: interfaces.py 49953 2008-02-06 20:22:05Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49953 $"
 
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

