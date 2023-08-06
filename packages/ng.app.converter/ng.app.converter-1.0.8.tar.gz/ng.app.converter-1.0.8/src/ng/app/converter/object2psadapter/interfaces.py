### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based object2psadapter package

$Id: interfaces.py 50493 2008-02-02 14:04:30Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50493 $"
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


