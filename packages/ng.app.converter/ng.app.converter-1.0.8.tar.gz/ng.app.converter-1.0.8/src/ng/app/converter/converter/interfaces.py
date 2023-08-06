### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converter interface

Interfaces for the Zope 3 based converter package

$Id: interfaces.py 49862 2008-01-06 22:27:04Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49862 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Float
from zope.app.container.interfaces import IContained, IContainer
from zope.app.component.interfaces import ILocalSiteManager, ISiteManagementFolder
from zope.app.container.constraints import ContainerTypesConstraint

class IConverter(Interface):
    """ A converter object """

    def convert(s):
        """Make a convertion"""
        pass

    mtime = Float(title = u"Last modification time", default=0.0, readonly=True)

class IConverterContained(IContained) :
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager,ISiteManagementFolder,IConverter))
        