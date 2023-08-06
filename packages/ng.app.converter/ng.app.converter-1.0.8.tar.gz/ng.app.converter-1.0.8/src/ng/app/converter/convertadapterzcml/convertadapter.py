### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertadapter

$Id: convertadapter.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.interface import implements
from object2psadapter.object2psadapter import Object2PSadapterBase

class ConvertAdapter(Object2PSadapterBase):
    """ """
    
    def __init__(self, object):
        super(ConvertAdapter, self).__init__(object)
