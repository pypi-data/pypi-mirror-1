### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterlightrest class.

$Id: converterlightrest.py 52364 2009-01-16 19:33:06Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52364 $"

from zope.interface import implements
from interfaces import IConverterLightReST
from ng.app.converter.converter.convertermultiregexpbase import ConverterMultiRegexpBase
from ng.app.converter.converter.interfaces import IConverter

class ConverterLightReST(ConverterMultiRegexpBase):
    __doc__ = IConverterLightReST.__doc__
    implements(IConverterLightReST,IConverter)
    
    title = ""
    use_html_filter = True
    

    @property
    def _rule_000(self) :
        if self.use_html_filter :
            return ('&','&amp;')
        return None            

    @property
    def _rule_001(self) :
        if self.use_html_filter :
            return ('<','&lt;')
        return None            

    @property
    def _rule_002(self) :
        if self.use_html_filter :
            return ('>','&gt;')
        return None            
#(?<!^\\)
    _rule_010 = (r'(^|(?<=\n\n))(?<![^\\]\\)[0-9]+\.\s*(?P<par>(.|(?<=[^\n])\n(?=[^\n]))*)((?=\n\n)|$)', '<conv:oli>%(par)s</conv:oli>')
    
    _rule_020 = (r'(^|(?<=\n\n))(?<![^\\]\\)[\-+]\s*(?P<par>(.|(?<=[^\n])\n(?=[^\n]))*)((?=\n\n)|$)', '<conv:uli>%(par)s</conv:uli>')
    
    _rule_030 = (r'\\(?=[0-9\-+])','')

    _rule_040 = (r'(^|(?<=\n\n))(?!<conv:[uo]li>)(?P<par>(.|(?<=[^\n])\n(?=[^\n]))*)((?=\n\n)|$)', '<p>%(par)s</p>')

    _rule_050 = (r'(?<=conv:oli>)(?P<par>\s*?)(?=<conv:oli)', '<conv:osp>%(par)s</conv:osp>')

    _rule_060 = (r'(?<=conv:uli>)(?P<par>\s*?)(?=<conv:uli)', '<conv:usp>%(par)s</conv:usp>')

    _rule_070 = (r'</conv:oli>(?!<conv:osp>)', '</conv:oli></ol>')

    _rule_080 = (r'</conv:uli>(?!<conv:usp>)', '</conv:uli></ul>')

    _rule_090 = (r'(?<!</conv:osp>)<conv:oli>', '<ol><conv:oli>')

    _rule_100 = (r'(?<!</conv:usp>)<conv:uli>', '<ul><conv:uli>')

    _rule_110 = (r'</?conv:[uo]sp>','')

    _rule_120 = (r'<(?P<par>/?)conv:[uo]li>', '<%(par)sli>')
    
    _rule_130 = (r'(?<!\\)\*(?<!\\)\*(?=[^\s*])(?P<par>.*?)(?<=[^\s*\\])\*(?<!\\)\*','<b>%(par)s</b>')

    _rule_140 = (r'(?<!\\)\*(?=[^\s*])(?P<par>.*?)(?<=[^\s*\\])\*','<i>%(par)s</i>')

    _rule_150 = (r'\\\*','*')

if __name__ == '__main__' :
    import sys
    print ConverterLightReST().convert(unicode(sys.stdin.read()))
