### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertadapterdirective interface

$Id: metadirectives.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"

from zope.interface import implements,Interface

class IConvertAdapter(Interface):
    
    # XXX Впишите докстринг
    # XXX Впишите все атрибуты и функции
    
    for_ = GlobalInterface(
                            title = u"Begin interface",
                            description = u"Interface",
                            required = True
                            )
    
    provides = GlobalInterface(
                            title = u"Provide interface",
                            description = u"Interface",
                            required = True
                            )

class IAttributeConvertAdapter(Interface):
    
    name = TextLine(        
                            title = u"Attribute's name",
                            description = u"Attribute's name",
                            required = True
                            )
    converter = TextLine(        
                            title = u"Attribute's converter",
                            description = u"Attribute's converter",
                            required = True
                            )
    src = TextLine(        
                            title = u"Attribute's source",
                            description = u"Attribute's source",
                            required = True
                            )