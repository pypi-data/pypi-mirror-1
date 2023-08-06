### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterrest interface

Interfaces for the Zope 3 based converterrest package

$Id: interfaces.py 52365 2009-01-16 20:12:22Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 52365 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Int, Bool, Choice
from zope.app.container.interfaces import IContained, IContainer
from ng.app.converter.converter.interfaces import IConverter
from zope.schema.vocabulary import SimpleVocabulary


class IConverterReSTAdd(Interface) :
    """ A converterrest interface"""
    
    title = TextLine(
                title = u"Title",
                default=u"Converter ReST"
                )

    input_encoding = TextLine(
                title = u"Input Encoding",
                default=u"unicode"
                )

    output_encoding = TextLine(
                title = u"Output Encoding",
                default=u"unicode"
                )

    initial_header_level = Choice(
                title = u"Initial Header Level",
                description= u'Specify the initial header level.  Default is 1 for "<h1>".  '
                        u'Does not affect document title & subtitle',
                default = 3,
                vocabulary = SimpleVocabulary.fromValues([1,2,3,4,5,6]),
                )                        
                
    halt_level = Choice(
                title = u"Halt Level",
                default = 6,
                vocabulary = SimpleVocabulary.fromValues([1,2,3,4,5,6]),
                )

    language_code = TextLine(
                title = u"Language",
                default=u"en"
                )

    embed_stylesheet = Bool(
                title = u"Use embeded stylesheet",
                default=True
                )
                
    stylesheet_path = TextLine(
                title = u"Link to stylesheet",
                default=u"/@@/style_rest.css"
                )


    field_name_limit = Int(
                title = u'Field name limit',
                description = 
	                u'Specify the maximum width (in characters) for one-column field '
                    u'names.  Longer field names will span an entire row of the table '
                    u'used to render the field list.  Default is 14 characters.  '
                    u'Use 0 for "no limit".',
                default = 14
                )                    

    option_limit = Int(
                title = u'Option Limit',
                description = 
	                u'Specify the maximum width (in characters) for options in option '
                    u'lists.  Longer options will span an entire row of the table used '
                    u'to render the option list.  Default is 14 characters.  '
                    u'Use 0 for "no limit"',
                default = 14
                )

    footnote_references = Choice(
            title = u'Footnote references format',
            description = 
                    u'Format for footnote references: one of "superscript" or '
                    u'"brackets".  Default is "brackets".',
            vocabulary = SimpleVocabulary.fromValues(['superscript', 'brackets']),
            default = 'brackets'
            )
            
    attribution = Choice(
            title = u"Block quote attributions format",
            description =
                u'Format for block quote attributions: one of "dash" (em-dash '
                u'prefix), "parentheses"/"parens", or "none".  Default is "dash".',
            vocabulary = SimpleVocabulary.fromValues(['dash', 'parentheses', 'parens', 'none']),
            default = 'dash'
            )

    compact_lists = Bool(
            title = u'Use compact lists',
            description = 
                u'Remove extra vertical whitespace between items of "simple" bullet '
                u'lists and enumerated lists.  Default: enabled.',
            default = True
            )                

    compact_field_lists = Bool(
            title = u'Use compact field lists',
            description = 
                u'Remove extra vertical whitespace between items of simple field '
                u'lists.  Default: enabled.',
            default =  True
            )                

    xml_declaration = Bool(
            title = u'Use the xml declaration',
            description = u'Omiting the XML declaration can cause unexpected failure.  Use with caution.',
            default=True
            )

    cloak_email_addresses = Bool(
            title = u'Cloak email addresses',
            description = 
                u'Obfuscate email addresses to confuse harvesters while still '
                u'keeping email links usable with standards-compliant browsers.',
            default = True
            )

class IConverterReST(IConverter,IConverterReSTAdd):
    """ A converterrest interface"""