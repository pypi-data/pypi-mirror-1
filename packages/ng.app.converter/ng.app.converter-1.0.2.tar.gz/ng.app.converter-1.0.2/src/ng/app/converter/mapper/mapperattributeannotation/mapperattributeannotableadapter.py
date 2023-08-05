### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The mapperattributeannotable adapter.

$Id: mapperattributeannotableadapter.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from ng.app.converter.mapper.mapperattribute.mapperattribute import MapperAttribute
from zope.annotation.interfaces import IAnnotations 

from interfaces import mapperattributeannotationkey

def MapperAttributeAnnotableAdapter(context) :
    return IAnnotations(context).setdefault(mapperattributeannotationkey,MapperAttribute())