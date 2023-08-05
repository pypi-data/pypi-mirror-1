### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: test.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"

                    

class Test(object) :

    def getData(self,*kv,**kw) :
        return {"text":""}

    def setData(self,d,**kw) :
        return self.context.convert(d["text"])
        
