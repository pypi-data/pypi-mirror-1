### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterrest class.

$Id: converterrest.py 52356 2009-01-15 15:53:27Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 52356 $"

from zope.interface import implements
from interfaces import IConverterReST
from ng.app.converter.converter.converter import ConverterBase
from ng.app.converter.converter.interfaces import IConverter
from docutils.writers.html4css1 import Writer
from docutils.writers.html4css1 import HTMLTranslator
import docutils 
import docutils.core

class ConverterReST(ConverterBase):
    __doc__ = IConverterReST.__doc__
    
    title = u"ConverterReST"
    halt_level = 6
    input_encoding = "unicode"
    output_encoding = 'unicode'
    initial_header_level = 3
    language_code = 'en'
    embed_stylesheet = True
    stylesheet_path = '/@@/style_rest.css'                
    field_name_limit = 14
    option_limit = 14
    footnote_references = 'brackets'
    attribution = 'dash'
    compact_lists = True
    compact_field_lists = True
    xml_declaration = True
    cloak_email_addresses = True
    
    def convert(self,text):
        if not text :
            return ""
            
        text = super(ConverterReST,self).convert(text)
        writer = Writer()
        writer.translator_class = HTMLTranslator
        html = docutils.core.publish_string(
            text,
            writer=writer,
            settings_overrides=dict(
                  (
                    ('halt_level', self.halt_level),
                    ('input_encoding', self.input_encoding),
                    ('output_encoding', self.output_encoding),
                    ('initial_header_level', self.initial_header_level),
                    ('language_code' , self.language_code),
                    ('embed_stylesheet' , self.embed_stylesheet),
                    ('field_name_limit', self.field_name_limit),
                    ('option_limit', self.option_limit),
                    ('footnote_references', self.footnote_references),
                    ('attribution', self.attribution),
                    ('compact_lists', self.compact_lists),
                    ('compact_field_lists', self.compact_field_lists),
                    ('xml_declaration', self.xml_declaration),
                    ('cloak_email_addresses', self.cloak_email_addresses),
                  ) + (not self.embed_stylesheet and ('stylesheet_path', self.stylesheet_path) or ())
                )
            )
        return html

    implements(IConverterReST,IConverter)

if __name__ == '__main__' :
    import sys
    print ConverterReST().convert(unicode(sys.stdin.read()))
