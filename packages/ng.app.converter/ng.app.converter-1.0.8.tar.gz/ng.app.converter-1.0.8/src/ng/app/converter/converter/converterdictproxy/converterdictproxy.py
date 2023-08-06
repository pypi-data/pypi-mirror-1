### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The converterlightrest class.

$Id: converterdictproxy.py 53403 2009-07-10 03:22:16Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53403 $"

from zope.interface import implements
from interfaces import IConverterDictProxy
from ng.app.converter.converter.convertermultiregexpbase import ConverterMultiRegexpBase
from ng.app.converter.converter.interfaces import IConverter
import re

basesubs = ""
class ConverterDictProxy(ConverterMultiRegexpBase):
    __doc__ = IConverterDictProxy.__doc__
    implements(IConverterDictProxy,IConverter)
    
    def convert(self,text,baseurl="") :
        global basesubs
        basesubs = baseurl
        proxiedtext = super(ConverterDictProxy,self).convert(text) #(?<!script)(?<!style)
        onclicktext = re.sub("(?<=>)[^<]*(?=<)(?!</a>|</title>|</style>|</script>)",
                lambda x : re.sub("(?<!&)(?<!&#)(^|(?<=\W))(?P<word>\w+)(?!=;)($|(?=\W))",
                      lambda x : u"""<span onclick="translate(event,'%(word)s');">%(word)s</span>""" % x.groupdict(),x.group()),
                proxiedtext)
        return onclicktext.replace("</head>",
"""<link href="http://dictlearn.dreambot.ru/@@/style_translate.css" rel="stylesheet" type="text/css" />
                  
   <script language="JavaScript" type="text/javascript" src="http://dictlearn.dreambot.ru/@@/cookie.js"></script>
                                  
   <script language="JavaScript" type="text/javascript" src="http://dictlearn.dreambot.ru/@@/query.js"></script>
                                                  
   <script language="JavaScript" type="text/javascript" src="http://dictlearn.dreambot.ru/@@/translate.js"></script>

   <div id="translate">
     <div id="translateslot" onclick="hidden(event); return true;" onmouseup="hidden(event); return true;">
       Здесь появится текст перевода
     </div>
     <div id="comment">Выделите перевод мышкой, чтобы добавить его в обучающающую выборку</div>
     <div id="queryfull">К списку добавлено <span id="newwords">0</span> новых слов, попробуйте
       <a href="javascript:opentrainer()" onclick="hidden(event); return true;">запустить тренажер</a>
     </div>
    </div>
</head>""",1)                

    title = ""
    prefix = "/@@proxy"
    
    _rule_000 = (r'<base[^>]+>','')

    @property
    def _rule_010(self) :
        return (r'(?P<prefix><\s*(frame|a)\s+[^>]*(src|href)=)"(?P<href>/[^"]*)"','%(prefix)s"' + self.prefix + '?href=' + basesubs + '%(href)s"')

    @property
    def _rule_020(self) :
        return (r'(?P<prefix><\s*(frame|a)\s+[^>]*(src|href)=)"(?P<href>http://[^"]+)"','%(prefix)s"' + self.prefix + '?href=%(href)s"')


    @property
    def _rule_030(self) :
        return (r'(?P<prefix><\s*(script|style|link|img)\s+[^>]*(href|src)=[\'"])(?P<href>/[^\'"]+)','%(prefix)s' + basesubs + '%(href)s"')

    @property
    def _rule_040(self) :
        return (r'(?P<prefix>@import\s+url\(\')(?P<href>/[^\']+)','%(prefix)s' + basesubs + '%(href)s')

    @property
    def _rule_050(self) :
        return (r'(?P<prefix>@import\s+[\'"])(?P<href>/[^\'"]+)','%(prefix)s' + basesubs + '%(href)s')

#    _rule_040 = (r"(?P<word>\w+)",u"""<span onclick="translate(event,'%(word)s');">%(word)s</span>""")

if __name__ == '__main__' :
    import sys
    print ConverterDictProxy().convert(unicode(sys.stdin.read()))
