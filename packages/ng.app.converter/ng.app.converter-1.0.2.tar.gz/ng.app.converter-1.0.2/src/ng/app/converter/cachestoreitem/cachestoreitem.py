### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The cachestoreitem class.

$Id: cachestoreitem.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.interface import implements
from persistent import Persistent
from ng.app.converter.cachestore.interfaces import ICachestoreContent
from interfaces import ICachestoreItem,ICachestoreItemContained
import time

class CachestoreItemBase(object):
    """Implementation of converted attribute"""

    implements(ICachestoreItem, ICachestoreContent, ICachestoreItemContained)

    def __init__(self, attribute = None, value = None, converter = None, mtime = None):
        self.attribute = attribute
        self.value = value
        self.converter = converter
        if not mtime :
            mtime = time.time()
        self.mtime = mtime
    
class CachestoreItem(CachestoreItemBase,Persistent):
    pass
