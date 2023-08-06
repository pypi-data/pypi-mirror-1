### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The MixIn class used to count some cache statistics 

$Id: statistic.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Andrey Orlov,2006"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class Statistic(object) :
        
    statistic_view = ViewPageTemplateFile("statistic.pt")

    def regenerate_all(self,*kv,**kw) :
        count,elapsed = self.context.regenerate_all()
        return self.statistic_view(self,count=count,elapsed=elapsed,*kv,**kw)

    def clean(self,*kv,**kw) :
        self.context.clean()
        return self.statistic_view(self,*kv,**kw)
        