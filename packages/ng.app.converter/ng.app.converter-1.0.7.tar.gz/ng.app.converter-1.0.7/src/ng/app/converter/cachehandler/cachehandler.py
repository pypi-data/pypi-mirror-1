### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of functions used to dispatch events to 
cache storage.

$Id: cachehandler.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.app import zapi
from ng.app.converter.cachestore.interfaces import ICachestore
from zope.component import ComponentLookupError

def regenerateHandler(ob,event) :
    try :
        for (name,cache) in zapi.getUtilitiesFor(ICachestore, ob) :
            cache.regenerate(ob)
    except ComponentLookupError,msg :
        print "ComponentLookupError",msg
        