### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterrest class.

$Id: converterrest.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

from zope.interface import implements
from interfaces import IConverterReST
from ng.app.converter.converter.converter import ConverterBase
from ng.app.converter.converter.interfaces import IConverter
from docutils.writers.html4css1 import Writer
from docutils.writers.html4css1 import HTMLTranslator
import docutils 

class ConverterReST(ConverterBase):
    __doc__ = IConverterReST.__doc__
    
    title = ""
    halt_level = 6
    input_encoding = "unicode"
    output_encoding = 'unicode'
    initial_header_level = 3
    
    def convert(self,text):
        if not text :
            return ""
            
        text = super(ConverterReST,self).convert(text)
        writer = Writer()
        writer.translator_class = HTMLTranslator
        html = docutils.core.publish_string(
            text,
            writer=writer,
            settings_overrides={
                'halt_level': self.halt_level,
                'input_encoding': self.input_encoding,
                'output_encoding': self.output_encoding,
                'initial_header_level': self.initial_header_level
                }
            )
        return html

    implements(IConverterReST,IConverter)

if __name__ == '__main__' :
    import sys
    print ConverterReST().convert(sys.stdin.read())
