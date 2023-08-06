### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterxslt class.

$Id: converterxslt.py 49830 2008-01-06 03:47:59Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49830 $"

from zope.interface import implements
from interfaces import IConverterXSLT
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.converter.converter import ConverterBase
import libxml2,libxslt,sys
from zope.app.file.interfaces import IFile
from zope.app.publication.interfaces import IFileContent
from zope.app.file.file import File
from chardet import detect

class ConverterXSLT(ConverterBase, File):
    """Converter for html with xslt schema"""

    implements(IConverterXSLT)
    
    """Charset for html input"""
    html_charset = None
    
    def __init__(self, context = None, html_charset = None):
	"""Constructor"""
        super(ConverterXSLT,self).__init__()
        self.html_charset = html_charset
        self.data = xsltsample
        self.contentType = 'text/plain'
        self._size = len(self.data)
	
    def xmlErrorHandler(self, ctx, msg) :
    	"""Handle an xml parse error"""
        print >>sys.stderr,"Xml Error: %s" % msg
    
    def convert(self, text) :
        """Convert and html with xslt schema"""
        text = super(ConverterXSLT,self).convert(text)
        xslt = libxslt.parseStylesheetDoc(libxml2.parseDoc(self.data))
        libxml2.registerErrorHandler(self.xmlErrorHandler,xslt)
        xml = libxml2.htmlParseDoc(text,self.html_charset)
        result = xslt.applyStylesheet(xml, None)
        return result.serialize().decode(result.htmlGetMetaEncoding())

xsltsample = """<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

      <!-- This template used to clean up html sources -->

      <xsl:template match="a">
        <xsl:copy>
          <xsl:apply-templates select="node()|attribute::href"/>
        </xsl:copy>
      </xsl:template> 

      <!-- <xsl:template match="img">
        <xsl:copy>
          <xsl:apply-templates select="node()|attribute::src"/>
        </xsl:copy>
      </xsl:template> -->

     <xsl:template match="meta">
        <xsl:copy>
          <xsl:apply-templates select="node()|attribute::*"/>
        </xsl:copy>
      </xsl:template> 

      <xsl:template match="p|h1|h2|h3|h4|h5|b|i|ul|ol|li|dl|dd|df|th|tr|td|table|body|html"> 
        <xsl:copy> 
          <xsl:apply-templates select="node()"/>
        </xsl:copy>
      </xsl:template>  

      <xsl:template match="img|div|span"> 
          <xsl:apply-templates select="node()"/>
      </xsl:template> 

      <xsl:template match="form|head|script|link|br|comment()|nobr"> 
	  <xsl:apply-templates select="meta"/>
      </xsl:template> 

      <xsl:template match="@*|node()">
        <xsl:copy> 
          <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
      </xsl:template> 

</xsl:stylesheet>
"""    


if __name__ == '__mainxslt__' :
    import getopt

    def do_xslt(html, xslt, out, html_charset=None):
        """Process conversion"""
        html_f = open(html)
        xslt_f = open(xslt)
        out_f = open(out,'w', 0)
        c = ConverterXSLT()
        c.data = xslt_f
        c.html_charset = html_charset
        out_f.write(c.convert(html_f.read()))

    def usage():
        """Usage"""
        print """usage: python converterxslt.py -source file.html -xslt scheme.xslt -out out.html [-charset utf-8]"""
    
    def go_out_usage():
        """Usage and exit"""
        usage()
        sys.exit(1)
   
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:x:o:c:h',['source', 'xslt', 'out', 'charset', 'help'])
    except getopt.GetoptError:
        go_out_usage()
    html = None 
    xslt = None
    charset = None
    out = None
   
    for opt, arg in opts:               
        if opt in ("-s", "--source"):     
            html = arg
        elif opt in ("-x", "--xslt"):
            xslt = arg
        elif opt in ("-c", "--charset"):
            charset = arg
        elif opt in ("-o", "--out"):
            out = arg
        elif opt in ("-h", "--help"):
            go_out_usage()

    
    if (html is None) or (xslt is None) or (out is None):
        go_out_usage()
    
    do_xslt(html, xslt, out, charset)