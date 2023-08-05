### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterxslt interface

Interfaces for the Zope 3 based converterxslt package

$Id: interfaces.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Anatoly Bubenkov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice, BytesLine, Bytes
from zope.app.container.interfaces import IContained, IContainer
from zope.app.file.interfaces import IFile
from zope.app.component.interfaces import ILocalSiteManager
from zope.app.container.constraints import ContainerTypesConstraint
from ng.app.converter.converter.interfaces import IConverter
from charsetvocabulary import charsetvocabulary 

class IConverterXSLT(IConverter):
    """Converter XSLT content"""
    
    html_charset = Choice(title = u'HTML Charset',
                          description = u'Select an charset',
                          required = False,
                          vocabulary = charsetvocabulary)
    

class IConverterXSLTSchema(IConverterXSLT, IFile):
    """Schema for IConverterXSLT"""
    
    html_charset = Choice(title = u'HTML Charset',
                          description = u'Select an charset',
                          required = False,
                          vocabulary = charsetvocabulary)
    
    contentType = BytesLine(
        title = u'XSLT Content Type',
        description=u'The content type identifies the type of data.',
        default='text/xml',
        required=False,
        missing_value='text/xml'
        )
        
    data = Bytes(
        title=u'XSLT Data',
        description=u'The actual content of the XSLT.',
        default='',
        missing_value='',
        required=True
        )

