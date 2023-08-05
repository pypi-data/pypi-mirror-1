### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: test.py 49876 2008-02-02 14:18:55Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49876 $"

                    

class Test(object) :

    def getData(self,*kv,**kw) :
        return {"text":""}

    def setData(self,d,**kw) :
        return self.context.convert(d["text"])
        
