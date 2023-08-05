### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based object2psadapter package

$Id: interfaces.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"
from zope.interface import Interface

class IPropertySheet(Interface):
    """ A Property Sheet interface """
    def __getitem__(value) :
        pass

    def get(name,default) :
        pass
        
    def keys() :
        pass
    
    def items() :
        pass
        
    def values() :
        pass
        
    def __str__() :
        pass

class IAttributeConvertable(Interface):
    """ A Attribute Covertable interface """
    pass


