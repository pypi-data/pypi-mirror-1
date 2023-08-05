### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: test.py 49600 2008-01-21 11:08:39Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49600 $"

                    

class Test(object) :

    def getData(self,*kv,**kw) :
        return {"text":""}

    def setData(self,d,**kw) :
        return self.context.convert(d["text"])
        
