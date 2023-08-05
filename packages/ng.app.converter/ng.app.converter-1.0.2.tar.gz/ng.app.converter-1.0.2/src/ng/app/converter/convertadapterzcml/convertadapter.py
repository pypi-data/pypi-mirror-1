### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertadapter

$Id: convertadapter.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.interface import implements
from object2psadapter.object2psadapter import Object2PSadapterBase

class ConvertAdapter(Object2PSadapterBase):
    """ """
    
    def __init__(self, object):
        super(ConvertAdapter, self).__init__(object)
