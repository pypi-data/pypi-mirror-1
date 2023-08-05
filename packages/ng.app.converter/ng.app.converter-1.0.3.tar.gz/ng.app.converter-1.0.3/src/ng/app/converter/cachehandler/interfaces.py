### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based cachehandler

$Id: interfaces.py 49876 2008-02-02 14:18:55Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49876 $"
 
from zope.interface import Interface
class ICacheStoreable(Interface):
    """ Marker interface used to sign the object can be used to be cached """
