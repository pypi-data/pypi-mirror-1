### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ConvertorST class for the Zope 3 based converterst package

$Id: converterst.py 50800 2008-02-21 11:13:08Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50800 $"
__date__ = "$Date: 2008-02-21 14:13:08 +0300 (Чтв, 21 Фев 2008) $"
 
from zope.interface import implements
from interfaces import IConverterST
from ng.app.converter.converter.converter import ConverterBase
from ng.app.converter.converter.interfaces import IConverter
from zope.app.renderer.stx import StructuredTextToHTMLRenderer
from zope.structuredtext.document import DocumentWithImages
from zope.structuredtext.html import HTMLWithImages
import re
                
class ConverterST(ConverterBase):
    __doc__ = IConverterST.__doc__

    implements(IConverterST,IConverter)
    
    def __init__(self):
        """ Initialization the converter by regexp, bytes and lines """

    def convert(self,text):
        """ Do convert """
        text = super(ConverterST,self).convert(text)        
        doc = DocumentWithImages()(text)
        html = HTMLWithImages()(doc)


        html = re.sub(
            r'(?sm)^<html.*<body.*?>\n(.*)</body>\n</html>\n',r'\1', html)                                
         
         
        return html
        #return html.decode("UTF-8")
            
        return StructuredTextToHTMLRenderer(text or "",None).render()
        
if __name__ == '__main__' :
    import sys
    print ConverterST().convert(sys.stdin.read())
    