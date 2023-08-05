### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based cachehandler

$Id: interfaces.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"
 
from zope.interface import Interface
class ICacheStoreable(Interface):
    """ Marker interface used to sign the object can be used to be cached """
