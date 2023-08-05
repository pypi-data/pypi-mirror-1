### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperattributeannotable adapter.

$Id: mapperattributeannotableadapter.py 49876 2008-02-02 14:18:55Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49876 $"

from ng.app.converter.mapper.mapperattribute.mapperattribute import MapperAttribute
from zope.annotation.interfaces import IAnnotations 

from interfaces import mapperattributeannotationkey

def MapperAttributeAnnotableAdapter(context) :
    return IAnnotations(context).setdefault(mapperattributeannotationkey,MapperAttribute())