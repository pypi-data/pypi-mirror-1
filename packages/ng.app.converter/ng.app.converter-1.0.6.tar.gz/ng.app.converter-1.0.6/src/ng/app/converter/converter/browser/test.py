### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: test.py 52356 2009-01-15 15:53:27Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 52356 $"

                    

class Test(object) :

    converted = ""
    show_source = False

    def getData(self,*kv,**kw) :
        return {"text":"", "show_source" : self.show_source}

    def setData(self,d,**kw) :
        self.converted = self.context.convert(d["text"])
        self.show_source = d["show_source"]
        return ""
        
