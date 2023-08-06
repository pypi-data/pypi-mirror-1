#! /usr/bin/python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Пример использования библиотек libxslt & libxml для выполнения xslt-преобразования
html-файла.
$Id: xslt.py 49773 2008-01-03 13:40:06Z cray $
"""
__version__ = '$Revision: 49773 $'[10:-1]
def _(s) : return s

import libxml2,libxslt,sys

def xmlErrorHandler(ctx,msg) :
    print >>sys.stderr,"Xml Error: %s" % msg
    
def do_xslt(html,xslt,html_charset=None) :
    xslt = libxml2.parseDoc(xslt)
    xslt = libxslt.parseStylesheetDoc(xslt)
    libxml2.registerErrorHandler(xmlErrorHandler,xslt)
    xml = libxml2.htmlParseDoc(html,html_charset)
    return xslt.applyStylesheet(xml, None).serialize()

if __name__ == '__main__' :
    import sys
    html = open(sys.argv[1]).read()
    xslt = open(sys.argv[2]).read()
        
    try :
        html_charset = sys.argv[3]
    except IndexError : 
        html_charset = None
                        
    print do_xslt(html,xslt,html_charset)
    

    